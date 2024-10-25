import uuid
from time import time
import streamlit as st

import utils.db as db
from utils.rag_hybrid import elastic_search_hybrid, build_prompt, llm, evaluate_relevance, calculate_openai_cost
# from utils.init_app_local import EMBEDDING_MODEL, ES_CLIENT, ES_INDEX, LLM_CLIENT, LLM_MODEL
from utils.init_app import EMBEDDING_MODEL, ES_CLIENT, ES_INDEX, LLM_CLIENT, LLM_MODEL


def generate_response(video_id, query, log_update_callback, n_results=4, context_col='smry_text', debug=0):
    logs = f"INFO: initiated response generation for video: {video_id} and query: {query}...\n"
    log_update_callback(logs)
    start_time = time()

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
    answer, token_stats = llm(prompt, LLM_CLIENT, LLM_MODEL)

    logs += "INFO: evaluating rag response's relevance...\n"
    log_update_callback(logs)
    relevance, rel_token_stats = evaluate_relevance(query, answer, LLM_CLIENT, LLM_MODEL)
    end_time = time()
    time_taken = end_time - start_time

    logs += "INFO: writing to database...\n"
    log_update_callback(logs)
    openai_cost_rag = calculate_openai_cost(LLM_MODEL, token_stats)
    openai_cost_eval = calculate_openai_cost(LLM_MODEL, rel_token_stats)
    openai_cost = openai_cost_rag + openai_cost_eval

    response_data = {
        "answer": answer,
        "model_used": LLM_MODEL,
        "response_time": time_taken,
        "relevance": relevance.get("Relevance", "UNKNOWN"),
        "relevance_explanation": relevance.get(
            "Explanation", "Failed to parse evaluation"
        ),
        "prompt_tokens": token_stats["prompt_tokens"],
        "completion_tokens": token_stats["completion_tokens"],
        "total_tokens": token_stats["total_tokens"],
        "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
        "eval_completion_tokens": rel_token_stats["completion_tokens"],
        "eval_total_tokens": rel_token_stats["total_tokens"],
        "openai_cost": openai_cost,
    }

    db.save_conversation(
        conversation_id=st.session_state["conversation_id"],
        video_id = video_id,
        question=query,
        response_data=response_data,
    )

    if debug:
        logs += f"DEBUG:\n\n\nSearch Results:\n{search_results}\n\n\nGenerated Prompt:\n {prompt}\n\n\nResponse Data:\n{response_data}\n"
        log_update_callback(logs)

    logs += f"INFO: response generated successfully for query: {query}\n"
    log_update_callback(logs)
    return f"Response:\n\n{response_data['answer']}", logs, response_data



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
            st.session_state["conversation_id"] = str(uuid.uuid4())
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
                    response, final_logs, response_data = generate_response(selected_video, user_query, update_logs)

                    # update session state to log with feedback
                    st.session_state["selected_video"] = selected_video
                    st.session_state["user_query"] = user_query
                    st.session_state["response"] = response
                    st.session_state["final_logs"] = final_logs
                    st.session_state["response_data"] = response_data

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
                            RAG Response Data: {st.session_state['response_data']} \n\n
                            Rating: {rating} \n Feedback: {feedback}""")
                db.save_feedback(
                    conversation_id=st.session_state["conversation_id"],
                    rating=rating,
                    feedback=feedback,
                )
    
    if "final_logs" in st.session_state:
        with st.expander("View Response Logs", expanded=False):
            st.text_area("Response Logs", value=st.session_state["final_logs"], height=200, disabled=st.session_state["disable_content"])

show_aibot_ui()
