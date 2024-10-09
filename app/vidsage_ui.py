import streamlit as st


home = st.Page("home.py", title="Home", icon="🏠")
add_vid = st.Page("add_video.py", title="Add Video", icon="📜")
rag_bot = st.Page("ai_assistant.py", title="AI Assistant", icon="🤖")
# st.v("vid_analytics.py", label="Video Insights", icon="📊", disabled=True)

pg = st.navigation([home, add_vid, rag_bot])
st.set_page_config(page_title="VidSage", page_icon="💬")
pg.run()
