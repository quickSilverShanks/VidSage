import time
import streamlit as st


def fetch(video_id):
    # Simulate the fetch process step by step
    logs = f"Fetching transcript for Video ID: {video_id}...\n"
    yield logs
    time.sleep(1)  # Simulate delay

    # Simulate intermediate step
    logs = "Connecting to video database...\n"
    yield logs
    time.sleep(1)

    # Simulate successful fetching
    fetched_data = f"Transcript data for {video_id}"
    logs = "Transcript fetched successfully.\n"
    yield logs

    # Update session state video ids list
    logs = f"Available video options: {st.session_state['video_options']}\n"
    yield logs

    if video_id not in st.session_state['video_options']:
        st.session_state['video_options'].append(video_id)
        logs = f"Video options updated: {st.session_state['video_options']}\n"
    else:
        logs = f"Video ID {video_id} already exists in the options.\n"

    yield logs

    # Final data fetched (you can return or yield as necessary)
    yield fetched_data



def show_addvideo_ui():
    col1, col2 = st.columns([1, 6])     # create two columns: one for the image and one for the title

    with col1:
        st.image("logo.jpg", width=80)
    
    with col2:
        st.markdown(
            """
            <h1 style='font-size:24px;'>VidSage: AI-Powered YouTube Video Assistant</h1>
            """, unsafe_allow_html=True
        )
    
    video_id = st.text_input("New Video ID", value="", label_visibility="visible")
    log_area = st.empty()       # text area to display logs

    if st.button('Fetch'):
        if video_id:
            log_text = ""  # initialize log text

            # fetch data and update logs dynamically
            for log in fetch(video_id):
                log_text += log  # append new log line
                log_area.text_area("Fetch Logs", value=log_text, height=200, disabled=True)
                time.sleep(0.5)  # add a small delay to simulate on-the-fly logging

            st.success(f"Fetch completed for: {video_id}")
        else:
            st.error("Please enter a Video ID")



show_addvideo_ui()
