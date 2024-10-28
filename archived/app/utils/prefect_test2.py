# from ingest_data_prefect import ingest_ytscript
from ingest_data_prefect2 import ingest_ytscript
from prefect import flow

# ingest_ytscript("MLKrmw906TM", "./data/summary_transcripts/tscribe_vid_MLKrmw906TM.json")
# ingest_ytscript("5C-s4JrymKM", "./data/summary_transcripts/tscribe_vid_5C-s4JrymKM.json")

@flow(log_prints=True)
def fetch(video_id):
    tscribe_vid_data = "./data/summary_transcripts/tscribe_vid_kXhJ3hHK9hQ.json"
    for ingest_log in ingest_ytscript(video_id, tscribe_vid_data):
        print(ingest_log)

fetch("kXhJ3hHK9hQ")
