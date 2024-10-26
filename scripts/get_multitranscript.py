import json
import click
from ingest_data import *
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


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



def load_jsonfile(filename):
    '''
    filename : filepath and filename(.json file) as a single string
    This function can be used to read any json file
    '''
    with open(filename, 'rt') as f:
        data_json = json.load(f)
    return data_json



def export_df_to_json(df, filename):
    '''
    df : the dataframe that needs to be dumped as json
    filename : string path and name of the destination json file
    '''
    df_json = df.to_dict(orient="records")
    with open(filename, 'wt') as f_out:
        json.dump(df_json, f_out, indent=2)



def index_doc(filename, index_name):
    documents = load_jsonfile(filename)

    print(f"INFO: creating vector embeddings")
    for doc in documents:
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
    for doc in documents:
        es_client.index(index=index_name, document=doc)
    
    print(f"INFO: added {len(documents)} documents to index")



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



def process_and_index_video(video_id, index_name, filepath):
    """
    Process the video transcript for the provided video_id and index it into Elasticsearch.
    
    Args:
        video_id (str): The video ID to process.
        
    Returns:
        None
    """
    if os.path.exists(filepath+"/tscribe_vid_"+video_id+".json"):
        print(f"INFO: processed transcript data exists for video_id: {video_id}")
    else:
        print(f"INFO: processing transcript data for video_id: {video_id}")
        process_transcript(video_id, filepath)

    print(f"INFO: indexing data for video_id: {video_id}")
    index_doc(filepath+"/tscribe_vid_"+video_id+".json", index_name)



def check_and_index_video(video_id, index_name, filepath):
    """
    If provided index_name does not exist, it will be created.
    Checks if the provided video_id's data is already indexed in Elasticsearch.
    If not, processes and indexes the video data.
    """
    if not es_client.indices.exists(index=index_name):
        print(f"INFO: index does not exist.")
        es_client.indices.create(index=index_name, body=INDEX_SETTINGS)
        print(f"INFO: index '{index_name}' created.")
        print(f"INFO: processing and indexing data for video_id {video_id}...")
        process_and_index_video(video_id, index_name, filepath)
    elif is_video_id_indexed(video_id, index_name):
        print(f"INFO: data for video_id {video_id} is already indexed.")
    else:
        print(f"INFO: data for video_id {video_id} not found. processing and indexing...")
        process_and_index_video(video_id, index_name, filepath)



@click.command()
@click.option(
    "--inp",
    default="./data/vidsource.csv",
    help="Input csv filename with location which contains list of video_ids in a single column. \
    Video IDs can be found in url.\
    For instance, https://www.youtube.com/watch?v=2pWv7GOvuf0 has the video_id '2pWv7GOvuf0'"
)
@click.option(
    "--dest",
    default="../data/summary_transcripts",
    help="Location where the processed data will be saved"
)
@click.option(
    "--index_name",
    default="video-transcripts-vect",
    help="The ElasticSearch Index that will keep the processed transcript documents from specified youtube videos"
)
def multi_videosrt(inp, dest, index_name):
    df = pd.read_csv(inp)
    vlist = list(df.video_id)

    print(f"INFO: total number videos to index is {len(vlist)}.")
    for v_id in vlist:
        check_and_index_video(v_id, index_name, dest)

    print(f"INFO: creating combined document json file.")
    df_list=[]
    allfiles = [dest+"/tscribe_vid_"+v+".json" for v in vlist]
    for partf in allfiles:
        jfile_tmp = load_jsonfile(partf)
        df_tmp = pd.DataFrame(jfile_tmp)
        df_list.append(df_tmp)
    df_combined = pd.concat(df_list, ignore_index=True)

    export_df_to_json(df_combined, dest+"/multi_tscribe.json")
    print(f"INFO: combined document json file created.")


if __name__ == "__main__":
    multi_videosrt()