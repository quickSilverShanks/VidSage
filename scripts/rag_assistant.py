import click
from elasticsearch import Elasticsearch
from openai import OpenAI
from sentence_transformers import SentenceTransformer


llm_client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
)


VECTOR_MODEL = 'multi-qa-MiniLM-L6-cos-v1'
VECTOR_DIMS = 384
LLM_MODEL = 'gemma2:2b'
es_client = Elasticsearch('http://localhost:9200')
model = SentenceTransformer(VECTOR_MODEL)



def elastic_search_hybrid(query, query_vect, index_name, video_id, n_results=5):
    '''
    This function performs a hybrid text and vector-based search in Elasticsearch.
    It searches across multiple vector fields and text fields for the best matching documents.
    Several boosting parameters and scalars in this function can be later tuned for better performance.
    
    Args:
        query (str): The query text.
        index_name (str): The Elasticsearch index to search in.
        n_results (int): Number of results to return.
    
    Returns:
        List of documents matching the query.
    '''
    
    search_query = {
        "size": n_results,
        "query": {
            "bool": {
                "should": [     # "must" replaced by "should"; "should" gives equal weight to both queries
                    # Text search query on text fields
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["keywords^3", "text", "smry_text", "clean_text"],
                            "type": "best_fields",
                            "boost": 0.2  # Weight for text search
                        }
                    },
                    # Script score for vector similarity
                    {
                        "script_score": {
                            "query": {"match_all": {}},  # Matching all since it's vector scoring
                            "script": {
                                "source": """
                                    3 * cosineSimilarity(params.query_vector, 'kwords_smry_vector') +
                                    1 * cosineSimilarity(params.query_vector, 'text_vector') +
                                    2 * cosineSimilarity(params.query_vector, 'smry_vector') +
                                    2 * cosineSimilarity(params.query_vector, 'cleantext_vector') +
                                    2 * cosineSimilarity(params.query_vector, 'kwords_vector') +
                                    10
                                """,  # Combine similarities across vector fields
                                "params": {
                                    "query_vector": query_vect  # Query encoded to a vector
                                }
                            },
                            "boost": 8  # Weight for vector search
                        }
                    }
                ],
                "filter": [  # Filter to ensure only documents with uid starting with 'video_id'
                    {
                        "wildcard": {
                            "uid": {
                                "value": f"{video_id}__*"  # Using wildcard to match 'video_id' part in 'uid'
                            }
                        }
                    }
                ]
            }
        },
        "_source": ["uid", "text", "smry_text", "clean_text", "keywords"]  # Adjust returned fields as needed
    }

    # Execute the search query
    es_results = es_client.search(
        index=index_name,
        body=search_query
    )
    
    # Collect and return the results
    result_docs = []
    for hit in es_results['hits']['hits']:
        result_docs.append(hit['_source'])
    
    return result_docs



def build_prompt(query, search_results, context_col):
    '''
    This function creates a prompt using provided 'search_results' that can be used to generate llm response for the user provided 'query'.
    '''
    prompt_template = """
        You are provided with a YouTube video transcript. Your task is to answer the QUESTION based on the CONTEXT. 

        Instructions:
        - Use only facts from the CONTEXT when answering the QUESTION.
        - Keep the response concise and less than 100 words.
        - Avoid any form of praise or commentary. Avoid unnecessary words or your personal opinions.
        - If the answer is not present in the CONTEXT, respond with: "The video does not contain this information."

        Example:
        If the CONTEXT is: "The sky is blue due to Rayleigh scattering."
        And the QUESTION is: "Why is the sky blue?"
        The expected response would be: "The sky is blue due to Rayleigh scattering."

        QUESTION: {question}

        CONTEXT:
        {context}
        """.strip()

    context = ""
    
    for doc in search_results:
        context = context + f"{doc[context_col]}\n\n"
    
    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt



def llm(prompt, llm_model):
    '''
    This function uses 'llm_model' to generate response for the provided input 'prompt' to llm.
    '''
    response = llm_client.chat.completions.create(
        model=llm_model,
        messages=[{"role": "user", "content": prompt}],
        # temperature=0,    # remove randomness for deterministic output but not using it as it makes summary clumsy with phrases like 'you stated correctly...', 'you explained it well...' etc.
        seed=72
    )

    return response.choices[0].message.content



@click.command()
@click.option(
    "--query",
    help="User provided query that needs to be replied by RAG system"
)
@click.option(
    "--index_name",
    default="video-transcripts-vect",
    help="The ElasticSearch Index that will be queried for transcript documents to generate the RAG response"
)
@click.option(
    "--video_id",
    help="Video ID of the youtube video to query. It can be found in url.\
    For instance, https://www.youtube.com/watch?v=2pWv7GOvuf0 has the video_id '2pWv7GOvuf0'"
)
def rag_hybrid(query, index_name, video_id, context_col='smry_text', debug=0):
    print(f"INFO: encoding user query")
    query_vect = model.encode(query)
    print(f"INFO: searching ES index for retrieval")
    search_results = elastic_search_hybrid(query, query_vect, index_name, video_id, 4)
    print(f"INFO: building response generation prompt")
    prompt = build_prompt(query, search_results, context_col)
    print(f"INFO: generating llm response")
    answer = llm(prompt, llm_model=LLM_MODEL)
    if debug:
        print(f"DEBUG:\n\n\nSearch Results:\n{search_results}\n\n\nGenerated Prompt:\n {prompt}\n\n\nRAG Output:\n{answer}")
    # return answer
    print(f"INFO: RAG RESPONSE-- {answer}")



if __name__=="__main__":
    rag_hybrid()
