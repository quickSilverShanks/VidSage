import streamlit as st
# import utils.init_app_local as init_app
import utils.init_app as init_app


home = st.Page("home.py", title="Home", icon="🏠")
add_vid = st.Page("add_video.py", title="Add Video", icon="📜")
rag_bot = st.Page("ai_assistant.py", title="AI Assistant", icon="🤖")
# insights = st.Page("vid_analytics.py", title="Video Insights", icon="📊")

pg = st.navigation([home, add_vid, rag_bot])
st.set_page_config(page_title="VidSage", page_icon="💬")
pg.run()


if 'initialized' not in st.session_state:
    st.session_state.initialized = False        # session state for tracking initialization

sidebar_message = st.sidebar.empty()

if not st.session_state.initialized:
    with sidebar_message.container():
        with st.spinner("Initializing Application..."):
            init_app.initialize_list()
        
        sidebar_message.markdown(       # change the spinner to a "Ready..." message when done with init_app
            "<div style='background-color: #77aa44; padding: 7px; border-radius: 5px;'>"
            "<h7 style='margin: 0;'>Ready...</h7>"
            "</div>",
            unsafe_allow_html=True
        )

    st.session_state.initialized = True     # set the initialized flag to True to prevent reinitalization