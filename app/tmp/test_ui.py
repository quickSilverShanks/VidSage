import streamlit as st
import time

# List of video options for the dropdown menu
video_options = ['Video 1', 'Video 2', 'Video 3', 'Video 4']



# Define your UDF function (dummy implementation here)
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

    # Final data fetched (you can return or yield as necessary)
    yield fetched_data



# Function to handle "Generate Response" button
def generate_response(selected_video, user_query):
    logs = f"Generating response for video: {selected_video} and query: {user_query}...\n"
    time.sleep(2)  # Simulate delay in response generation
    logs += f"Response generated successfully for query: {user_query}\n"
    return f"Response for {selected_video} with query '{user_query}'", logs



# Streamlit app layout
def main():
    # Create two columns: one for the image and one for the title
    col1, col2 = st.columns([1, 6])  # Adjust the width ratio as per your needs

    # Add an image in the first column (col1)
    with col1:
        st.image("./app/logo.jpg", width=80)  # Replace with your image path and adjust the width

    # Add the title with custom font size in the second column (col2)
    with col2:
        st.markdown(
            """
            <h1 style='font-size:24px;'>VidSage: AI-Powered YouTube Video Assistant</h1>
            """, unsafe_allow_html=True
        )
    # st.title("VidSage: AI-Powered YouTube Video Assistant")

    # Left-aligned input text box for 'New Video ID'
    video_id = st.text_input("New Video ID", value="", label_visibility="visible")

    # Text area to display logs
    log_area = st.empty()  # Reserve an area for the logs

    # 'Fetch' button that calls the fetch function
    if st.button('Fetch'):
        if video_id:
            log_text = ""  # Initialize log text

            # Fetch data and update logs dynamically
            for log in fetch(video_id):
                log_text += log  # Append new log line
                log_area.text_area("Fetch Logs", value=log_text, height=200, disabled=True)
                time.sleep(0.5)  # Add a small delay to simulate on-the-fly logging

            st.success(f"Fetch completed for: {video_id}")
        else:
            st.error("Please enter a Video ID")

    # Dropdown menu for 'Select Video'
    selected_video = st.selectbox('Select Video', video_options)

    # Input text box for 'User Query'
    user_query = st.text_input('User Query')

    # Placeholder for response generation status
    response_status_area = st.empty()

    # 'Generate Response' button
    if st.button('Generate Response'):
        if selected_video and user_query:
            # Display "Generating Response..." in a highlighted (colored) text area
            response_status_area.markdown("<div style='background-color:#77aa44;padding:10px;'>Generating Response...</div>", unsafe_allow_html=True)

            # Simulate response generation and log capturing
            response, response_logs = generate_response(selected_video, user_query)

            # Once the response is generated, clear the "Generating Response..." message
            response_status_area.empty()  # Collapse the message

            # Display the actual response in a shaded box
            st.info(response)

            # Display logs in a collapsible expander section
            with st.expander("View Response Logs", expanded=False):
                st.text_area("Response Logs", value=response_logs, height=200, disabled=True)
        else:
            st.error("Please select a video and enter a query")

# Run the app
# if __name__ == '__main__':
#     main()

main()
