import streamlit as st
import time


def generate_response(selected_video, user_query, log_update_callback):
    logs = f"Generating response for video: {selected_video} and query: {user_query}...\n"
    log_update_callback(logs)  # Update logs in the UI
    time.sleep(1)  # Simulate delay in response generation

    logs += "Analyzing video content...\n"
    log_update_callback(logs)
    time.sleep(1)

    logs += "Processing user query...\n"
    log_update_callback(logs)
    time.sleep(1)

    logs += f"Response generated successfully for query: {user_query}\n"
    log_update_callback(logs)
    return f"Response for {selected_video} with query '{user_query}'", logs


def show_aibot_ui():
    col1, col2 = st.columns([1, 6])  # Create two columns: one for the image and one for the title

    with col1:
        st.image("logo.jpg", width=80)

    with col2:
        st.markdown(
            """
            <h1 style='font-size:24px;'>VidSage: AI-Powered YouTube Video Assistant</h1>
            """, unsafe_allow_html=True
        )

    selected_video = st.selectbox('Select Video', st.session_state['video_options'])
    user_query = st.text_input('User Query')

    # Create a two-column layout for the button and spinner
    button_col, spinner_col = st.columns([2, 4])
    response_status_area = st.empty()  # Placeholder for response generation status
    log_area = st.empty()  # Placeholder for active log updates below the button
    button_disabled = False

    # Place the button in the first column
    with button_col:
        generate_button = st.button('Generate Response', disabled=button_disabled)

    # The spinner will be shown on the right side of the button during processing
    with spinner_col:
        spinner_placeholder = st.empty()

    if generate_button:
        if selected_video and user_query:
            button_disabled = True  # Disable button to prevent multiple clicks

            # Display a spinner on the right side of the button
            with spinner_placeholder:
                with st.spinner("Generating..."):
                    response_logs = ""

                    # Function to update the log area during generation
                    def update_logs(log_text):
                        nonlocal response_logs
                        response_logs = log_text
                        log_area.text_area("Active Logs", value=response_logs, height=200, disabled=True)

                    # Generate the response with real-time log updates
                    response, final_logs = generate_response(selected_video, user_query, update_logs)

            # Clear the active log area after response generation
            log_area.empty()

            # Clear the spinner placeholder after completion
            spinner_placeholder.empty()

            # Update the response status
            response_status_area.empty()  # Clear the "Generating Response..." message
            st.info(response)  # Display the actual response in a shaded box

            # Show logs in a collapsible section after completion
            with st.expander("View Response Logs", expanded=False):
                st.text_area("Response Logs", value=final_logs, height=200, disabled=True)

            button_disabled = False  # Re-enable the button after generation
        else:
            st.error("Please select a video and enter a query")


show_aibot_ui()
