import json
from tqdm import tqdm
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

VIDEO_ID = 'zjkBMFhNj_g'
INDEX_NAME = "video-transcripts-vect"
VECTOR_MODEL = 'multi-qa-MiniLM-L6-cos-v1'
VECTOR_DIMS = 384

es_client = Elasticsearch('http://localhost:9200')
model = SentenceTransformer(VECTOR_MODEL)

INDEX_SETTINGS = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "uid": {"type": "text"},
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


def load_jsonfile(filename):
    '''
    filename : filepath and filename(.json file) as a single string
    This function can be used to read any json file
    '''
    with open(filename, 'rt') as f:
        data_json = json.load(f)
    return data_json


def index_doc(filename, index_name):
    documents = load_jsonfile(filename)

    print(f"INFO: creating vector embeddings")
    for doc in tqdm(documents):
        text = doc['text']
        smry_text = doc['smry_text']
        clean_text = doc['clean_text']
        keywords = doc['keywords']
        kwords_smry = keywords + ' ' + smry_text

        doc['text_vector'] = model.encode(text)
        doc['smry_vector'] = model.encode(smry_text)
        doc['cleantext_vector'] = model.encode(clean_text)
        doc['kwords_vector'] = model.encode(keywords)
        doc['kwords_smry_vector'] = model.encode(kwords_smry)

    print(f"INFO: adding documents to index")
    for doc in tqdm(documents):
        es_client.index(index=index_name, document=doc)


def is_video_id_indexed(video_id, index_name):
    """
    Checks if the video_id is already indexed in the Elasticsearch index.
    
    Args:
        video_id (str): The video ID to check in Elasticsearch.
        index_name (str): The Elasticsearch index to search in. Default is "video-transcripts".
    
    Returns:
        bool: True if the video_id is indexed, False otherwise.
    """
    search_query = {
        "query": {
            "wildcard": {
                "uid": {
                    "value": f"{video_id}__*"  # Using wildcard to match 'video_id' part in 'uid'
                }
            }
        }
    }
    
    response = es_client.search(index=index_name, body=search_query)
    
    if response['hits']['total']['value'] > 0:
        return True
    return False


def process_and_index_video(video_id, index_name):
    """
    Process the video transcript for the provided video_id and index it into Elasticsearch.
    
    Args:
        video_id (str): The video ID to process.
        
    Returns:
        None
    """
    print(f"INFO: processing tarnscript data for video_id: {video_id}")
    # Placeholder: Implement the logic to extract, process, and save the video transcript as json document

    print(f"INFO: indexing data for video_id: {video_id}")
    index_doc("../data/summary_transcripts/tscribe_vid_"+video_id+".json", index_name)


def check_and_index_video(video_id, index_name):
    """
    Checks if the provided video_id's data is already indexed in Elasticsearch.
    If not, processes and indexes the video data.
    
    Args:
        video_id (str): The video ID to check and index if not found.
        index_name (str): The Elasticsearch index to check in. Default is "video-transcripts".
    
    Returns:
        None
    """
    if not es_client.indices.exists(index=index_name):
        print(f"INFO: index does not exist.")
        es_client.indices.create(index=index_name, body=INDEX_SETTINGS)
        print(f"INFO: index '{index_name}' created.")
        print(f"INFO: processing and indexing data for video_id {video_id}...")
        process_and_index_video(video_id, index_name)
    elif is_video_id_indexed(video_id, index_name):
        print(f"INFO: data for video_id {video_id} is already indexed.")
    else:
        print(f"INFO: data for video_id {video_id} not found. processing and indexing...")
        process_and_index_video(video_id, index_name)


# Example usage
check_and_index_video(VIDEO_ID, INDEX_NAME)