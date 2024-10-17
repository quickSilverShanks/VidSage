import json


def load_jsonfile(filename):
    '''
    filename : filepath and filename(.json file) as a single string
    This function can be used to read any json file
    '''
    with open(filename, 'rt') as f:
        data_json = json.load(f)
    return data_json



def index_doc(filename, model, es_client, index_name):
    documents = load_jsonfile(filename)

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

    for doc in documents:
        es_client.index(index=index_name, document=doc)



def is_video_id_indexed(video_id, es_client, index_name):
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
