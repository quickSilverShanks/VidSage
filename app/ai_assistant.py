import streamlit as st

from utils.rag_hybrid import elastic_search_hybrid, build_prompt, llm
from utils.init_app_local import EMBEDDING_MODEL, ES_CLIENT, ES_INDEX, LLM_CLIENT, LLM_MODEL
# from utils.init_app import EMBEDDING_MODEL, ES_CLIENT, ES_INDEX, LLM_CLIENT, LLM_MODEL


def generate_response(video_id, query, log_update_callback, n_results=4, context_col='smry_text', debug=0):
    logs = f"INFO: initiated response generation for video: {video_id} and query: {query}...\n"
    log_update_callback(logs)

    logs += "INFO: encoding user query...\n"
    log_update_callback(logs)
    query_vect = EMBEDDING_MODEL.encode(query)

    logs += "INFO: searching ES index for retrieval...\n"
    log_update_callback(logs)
    search_results = elastic_search_hybrid(query, query_vect, ES_CLIENT, ES_INDEX, video_id, n_results)

    logs += "INFO: building response generation prompt...\n"
    log_update_callback(logs)
    prompt = build_prompt(query, search_results, context_col)

    logs += "INFO: generating llm response...\n"
    log_update_callback(logs)
    answer = llm(prompt, LLM_CLIENT, LLM_MODEL)

    if debug:
        logs += f"DEBUG:\n\n\nSearch Results:\n{search_results}\n\n\nGenerated Prompt:\n {prompt}\n\n\nRAG Output:\n{answer}\n"
        log_update_callback(logs)

    logs += f"INFO: response generated successfully for query: {query}\n"
    log_update_callback(logs)
    return f"Response:\n\n{answer}", logs



def show_aibot_ui():
    st.session_state["disable_content"] = False
    col1, col2 = st.columns([1, 6])

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

    button_col, spinner_col = st.columns([2, 4])
    response_status_area = st.empty()   # placeholder for response generation status
    log_area = st.empty()               # placeholder for active log updates below the button

    with button_col:
        generate_button = st.button('Generate Response', disabled=st.session_state["disable_content"])

    with spinner_col:
        spinner_placeholder = st.empty()

    if generate_button:
        st.session_state["response"] = ""
        st.session_state["final_logs"] = ""
        if selected_video and user_query:
            st.session_state["disable_content"] = True

            with spinner_placeholder:
                with st.spinner("Generating..."):       # display a spinner on the right side of the button
                    response_logs = ""

                    # function to update the log area during generation
                    def update_logs(log_text):
                        nonlocal response_logs
                        response_logs = log_text
                        log_area.text_area("Active Logs", value=response_logs, height=200, disabled=True)

                    # generate the response with real-time log updates
                    response, final_logs = generate_response(selected_video, user_query, update_logs)

                    # update session state to log with feedback
                    st.session_state["selected_video"] = selected_video
                    st.session_state["user_query"] = user_query
                    st.session_state["response"] = response
                    st.session_state["final_logs"] = final_logs

            log_area.empty()                # clear the active log area after response generation
            spinner_placeholder.empty()     # clear the spinner placeholder after completion
            response_status_area.empty()    # clear the "Generating Response..." message

            st.session_state["disable_content"] = False         # enable interaction after response generation

        else:
            st.session_state["user_query"] = ""
            st.session_state["response"] = ""
            st.error("Please select a video and enter a query")

    # # display response(rag output)
    if "response" in st.session_state:
        st.info(st.session_state["response"])
    
    # # user feedback section
    with st.expander("User Feedback", expanded=False):
        rating = st.slider("Rate the quality of the answer (1: Poor, 5: Excellent)", 1, 5, 0, disabled=st.session_state["disable_content"])
        feedback = st.text_area("Additional feedback (optional)")

        if st.button("Submit Feedback", disabled=st.session_state["disable_content"]):
            if (st.session_state['user_query'] == "") or (st.session_state['response'] == ""):
                st.error("Please query the AI assistant first")
            elif rating==0:
                st.error("Please give a valid rating(0 is not valid)")
            else:
                st.success(f"""Thank you for the feedback. Your feedback has been recorded:\n\n 
                            Selected Video: {st.session_state['selected_video']} \n\n 
                            User query: {st.session_state['user_query']} \n\n 
                            AI Response: {st.session_state['response']} \n\n 
                            Rating: {rating} \n Feedback: {feedback}""")
    
    # if "final_logs" in st.session_state:
    with st.expander("View Response Logs", expanded=False):
        st.text_area("Response Logs", value=st.session_state["final_logs"], height=200, disabled=st.session_state["disable_content"])

show_aibot_ui()
