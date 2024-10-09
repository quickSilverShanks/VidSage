from elasticsearch import Elasticsearch

es_client = Elasticsearch('http://localhost:9200')

index_name = "video-transcripts-vect"


def get_vid_id_frequency(index_name):
    # Define the search query with terms aggregation on the extracted 'vid_id'
    search_query = {
        "size": 0,  # We don't need actual documents, just the aggregation result
        "aggs": {
            "vid_id_count": {
                "terms": {
                    "script": {
                        "source": """
                            String uid_value = doc['uid'].value;
                            return uid_value.substring(0, uid_value.indexOf('__'));
                            """,  # Script to extract vid_id part
                        "lang": "painless"
                    },
                    "size": 100  # Number of top 'vid_id's to return, adjust as needed
                }
            }
        }
    }

    # Perform the search with aggregation
    response = es_client.search(index=index_name, body=search_query)
    
    # Extract aggregation results
    buckets = response['aggregations']['vid_id_count']['buckets']
    
    # Prepare a dictionary of vid_id counts
    vid_id_counts = {bucket['key']: bucket['doc_count'] for bucket in buckets}
    
    return vid_id_counts

# Call the function and print vid_id frequency counts
vid_id_frequency = get_vid_id_frequency(index_name)
print(vid_id_frequency)
