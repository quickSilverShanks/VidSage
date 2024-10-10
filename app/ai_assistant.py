import streamlit as st
import time

video_options = ['Video 1', 'Video 2', 'Video 3', 'Video 4']



def generate_response(selected_video, user_query):
    logs = f"Generating response for video: {selected_video} and query: {user_query}...\n"
    time.sleep(2)  # Simulate delay in response generation
    logs += f"Response generated successfully for query: {user_query}\n"
    return f"Response for {selected_video} with query '{user_query}'", logs



def show_aibot_ui():
    col1, col2 = st.columns([1, 6])     # create two columns: one for the image and one for the title

    with col1:
        st.image("logo.jpg", width=80)
    
    with col2:
        st.markdown(
            """
            <h1 style='font-size:24px;'>VidSage: AI-Powered YouTube Video Assistant</h1>
            """, unsafe_allow_html=True
        )

    selected_video = st.selectbox('Select Video', video_options)
    user_query = st.text_input('User Query')

    response_status_area = st.empty()       # placeholder for response generation status

    if st.button('Generate Response'):
        if selected_video and user_query:
            response_status_area.markdown("<div style='background-color:#77aa44;padding:10px;'>Generating Response...</div>", unsafe_allow_html=True)

            # Simulate response generation and log capturing
            response, response_logs = generate_response(selected_video, user_query)

            response_status_area.empty()        # once the response is generated, clear the "Generating Response..." message

            st.info(response)       # display the actual response in a shaded box

            # display logs in a collapsible expander section
            with st.expander("View Response Logs", expanded=False):
                st.text_area("Response Logs", value=response_logs, height=200, disabled=True)
        else:
            st.error("Please select a video and enter a query")


show_aibot_ui()
