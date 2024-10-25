import os
from flask import Flask, render_template, request, jsonify
from utils.init_app import LANG, EMBEDDING_MODEL, ES_CLIENT, ES_INDEX, INDEX_SETTINGS, LLM_CLIENT, LLM_MODEL
from utils.es_indexer import is_video_id_indexed, index_doc
from utils.ingest_data import ingest_ytscript

app_getvid = Flask(__name__)

# Session state to simulate the behavior of Streamlit's session state
video_options = []



def fetch(video_id):
    logs = f"INFO: initiated transcript fetch for video id: {video_id}...\n"
    yield logs
    tscribe_vid_data = "./app_data" + f"/tscribe_vid_{video_id}.json"

    if not ES_CLIENT.indices.exists(index=ES_INDEX):  # Create index if not exists
        logs = f"INFO: index '{ES_INDEX}' does not exist, creating index...\n"
        yield logs
        ES_CLIENT.indices.create(index=ES_INDEX, body=INDEX_SETTINGS)

    if is_video_id_indexed(video_id, ES_CLIENT, ES_INDEX):
        logs = f"INFO: data for video_id {video_id} is already indexed, skipping data fetch...\n"
        yield logs
    else:
        if os.path.exists(tscribe_vid_data):
            logs = f"INFO: processed transcript data exists for video_id: '{video_id}', skipping data ingest...\n"
            yield logs
        else:
            logs = f"INFO: processed transcript for video_id '{video_id}' does not exist, initiating data ingest...\n"
            yield logs

            for ingest_log in ingest_ytscript(video_id, tscribe_vid_data, LANG, LLM_CLIENT, LLM_MODEL):
                yield ingest_log

        logs = f"INFO: indexing data for video_id: '{video_id}'...\n"
        yield logs
        index_doc(tscribe_vid_data, EMBEDDING_MODEL, ES_CLIENT, ES_INDEX)

    # Update video options
    logs = f"INFO: available video options: {video_options}\n"
    yield logs

    if video_id not in video_options:
        video_options.append(video_id)
        logs = f"INFO: video options updated: {video_options}\n"
    else:
        logs = f"INFO: requested video ID '{video_id}' already exists in the options.\n"

    yield logs



@app_getvid.route('/')
def home():
    return render_template('getvideo.html', video_options=video_options)



@app_getvid.route('/fetch', methods=['POST'])
def fetch_video():
    video_id = request.form.get('video_id')
    if not video_id:
        return jsonify({"error": "Please enter a Video ID"}), 400

    log_text = ""
    for log in fetch(video_id):
        log_text += log

    return jsonify({"message": f"Fetch completed for: {video_id}", "logs": log_text}), 200



if __name__ == '__main__':
    app_getvid.run(host='0.0.0.0', port=5000)
