import streamlit as st
import init_temp

init_temp.initialize_list()

home = st.Page("home.py", title="Home", icon="🏠")
add_vid = st.Page("add_video.py", title="Add Video", icon="📜")
rag_bot = st.Page("ai_assistant.py", title="AI Assistant", icon="🤖")
# insights = st.Page("vid_analytics.py", title="Video Insights", icon="📊")

pg = st.navigation([home, add_vid, rag_bot])
st.set_page_config(page_title="VidSage", page_icon="💬")
pg.run()
