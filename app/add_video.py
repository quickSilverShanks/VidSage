import os
import streamlit as st

from utils.init_app import LANG, EMBEDDING_MODEL, ES_CLIENT, ES_INDEX, INDEX_SETTINGS, LLM_CLIENT, LLM_MODEL
# from utils.init_app_local import LANG, EMBEDDING_MODEL, ES_CLIENT, ES_INDEX, INDEX_SETTINGS, LLM_CLIENT, LLM_MODEL
from utils.es_indexer import is_video_id_indexed, index_doc
from utils.ingest_data import ingest_ytscript


def fetch(video_id):
    logs = f"INFO: initiated transcript fetch for video id: {video_id}...\n"
    yield logs
    tscribe_vid_data = "./app_data"+"/tscribe_vid_"+video_id+".json"

    if not ES_CLIENT.indices.exists(index=ES_INDEX):        # ideally should not happen as its created while app initialization
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

    # update session state video ids list
    logs = f"INFO: available video options: {st.session_state['video_options']}\n"
    yield logs

    if video_id not in st.session_state['video_options']:
        st.session_state['video_options'].append(video_id)
        logs = f"INFO: video options updated: {st.session_state['video_options']}\n"
    else:
        logs = f"INFO: requested video ID '{video_id}' already exists in the options.\n"

    yield logs



def show_addvideo_ui():
    col1, col2 = st.columns([1, 6])

    with col1:
        st.image("logo.jpg", width=80)
    
    with col2:
        st.markdown(
            """
            <h1 style='font-size:24px;'>VidSage: AI-Powered YouTube Video Assistant</h1>
            """, unsafe_allow_html=True
        )
    
    video_id = st.text_input("New Video ID", value="", label_visibility="visible")
    log_area = st.empty()                   # text area to display logs

    if st.button('Fetch'):
        if video_id:
            log_text = ""                   # initialize log text

            for log in fetch(video_id):     # dynamic log update
                log_text += log
                log_area.text_area("Fetch Logs", value=log_text, height=200, disabled=True)

            st.success(f"Fetch completed for: {video_id}")
        else:
            st.error("Please enter a Video ID")



show_addvideo_ui()
