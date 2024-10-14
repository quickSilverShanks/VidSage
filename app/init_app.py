import streamlit as st
import time

def initialize_list():
    if 'video_options' not in st.session_state:
        # Initialize the list if it's not already present in session_state
        st.session_state['video_options'] = ['Video 1', 'Video 2', 'Video 3']
        time.sleep(10)

# Call the function to initialize
initialize_list()