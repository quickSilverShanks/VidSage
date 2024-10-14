import os
import json
# import ollama
from openai import OpenAI
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from utils.es_indexer import index_doc


ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
ES_INDEX = os.environ.get('ES_INDEX')
VECTOR_MODEL = os.environ.get('VECTOR_MODEL')
VECTOR_DIMS = os.environ.get('VECTOR_DIMS')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
LLM_MODEL = os.environ.get('LLM_MODEL')
OPENAI_API_URL = os.environ.get('OPENAI_API_URL')


INDEX_SETTINGS = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "uid": {"type": "keyword"},
            "text": {"type": "text"},
            "smry_text": {"type": "text"},
            "clean_text": {"type": "text"},
            "keywords": {"type": "text"},
            "text_vector": {
                "type": "dense_vector",
                "dims": VECTOR_DIMS,
                "index": True,
                "similarity": "cosine"
            },
            "smry_vector": {
                "type": "dense_vector",
                "dims": VECTOR_DIMS,
                "index": True,
                "similarity": "cosine"
            },
            "cleantext_vector": {
                "type": "dense_vector",
                "dims": VECTOR_DIMS,
                "index": True,
                "similarity": "cosine"
            },
            "kwords_vector": {
                "type": "dense_vector",
                "dims": VECTOR_DIMS,
                "index": True,
                "similarity": "cosine"
            },
            "kwords_smry_vector": {
                "type": "dense_vector",
                "dims": VECTOR_DIMS,
                "index": True,
                "similarity": "cosine"
            },
        }
    }
}



def initialize_id_list(index_name):

    tscribe_path = "./app_data/multi_tscribe.json"
    
    if os.path.exists(tscribe_path):
        index_doc(tscribe_path, EMBEDDING_MODEL, ES_CLIENT, index_name)       #index the initialization document

        # define the search query with terms aggregation on the extracted 'vid_id'
        search_query = {
            "size": 0,      # we don't need actual documents, just the aggregation result
            "aggs": {
                "vid_id_count": {
                    "terms": {
                        "script": {
                            "source": """
                                String uid_value = doc['uid'].value;
                                return uid_value.substring(0, uid_value.indexOf('__'));
                                """,        # script to extract vid_id part
                            "lang": "painless"
                        },
                        "size": 100     # number of top 'vid_id's to return, adjust as needed
                    }
                }
            }
        }

        response = ES_CLIENT.search(index=index_name, body=search_query)        # perform the search with aggregation
        buckets = response['aggregations']['vid_id_count']['buckets']       # extract aggregation results
        vid_id_counts = {bucket['key']: bucket['doc_count'] for bucket in buckets}      # dictionary of vid_id counts
        
        return list(vid_id_counts.keys())
    else:
        return []


# unable to connect to the ollama service
# ollama.pull(LLM_MODEL)

LLM_CLIENT = OpenAI(
    base_url=OPENAI_API_URL,
    api_key=OPENAI_API_KEY,
)

ES_CLIENT = Elasticsearch(ELASTICSEARCH_URL)

ES_CLIENT.indices.delete(index=ES_INDEX, ignore_unavailable=True)
ES_CLIENT.indices.create(index=ES_INDEX, body=INDEX_SETTINGS)

EMBEDDING_MODEL = SentenceTransformer(VECTOR_MODEL)
os.environ['ID_LIST'] = json.dumps(initialize_id_list(ES_INDEX))
