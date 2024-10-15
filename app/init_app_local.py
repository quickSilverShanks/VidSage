import os
import streamlit as st
from openai import OpenAI
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from utils.es_indexer import index_doc


# [LLM]
OPENAI_API_KEY =  "ollama"
OPENAI_API_URL = 'http://localhost:11434/v1/'
LLM_MODEL = 'gemma2:2b'

# [ElasticSearch]
ELASTICSEARCH_URL = "http://localhost:9200"
ES_INDEX = "video-transcripts-app"

# [Sentence Embedding]
VECTOR_MODEL = 'multi-qa-MiniLM-L6-cos-v1'
VECTOR_DIMS = 384

# [YouTube Transcript Config]
LANG = ['en', 'en-US', ]


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


def initialize_es_index(index_name):

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


LLM_CLIENT = OpenAI(
    base_url=OPENAI_API_URL,
    api_key=OPENAI_API_KEY,
)
ES_CLIENT = Elasticsearch(ELASTICSEARCH_URL)
EMBEDDING_MODEL = SentenceTransformer(VECTOR_MODEL)


def initialize_list():
    if 'video_options' not in st.session_state:
        # Initialize the list if it's not already present in session_state
        ES_CLIENT.indices.delete(index=ES_INDEX, ignore_unavailable=True)
        ES_CLIENT.indices.create(index=ES_INDEX, body=INDEX_SETTINGS)
        
        st.session_state['video_options'] = initialize_es_index(ES_INDEX)