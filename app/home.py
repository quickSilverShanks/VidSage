import streamlit as st

# page = st.sidebar.selectbox("VidSage", ('Home', 'Add Video', 'AI Assistant'))


# CSS to ensure the title stays on one line
st.markdown(
    """
    <style>
    .title-class {
        font-size: 2em; /* Adjust this if needed, but you don't need to hardcode small sizes */
        white-space: nowrap; /* Prevents the title from wrapping */
        overflow: hidden;
        text-overflow: ellipsis; /* Adds ... if it overflows */
    }
    </style>
    """,
    unsafe_allow_html=True
)



def show_home_page():

    st.image("logo.jpg")

    # apply the custom CSS class to the title
    st.markdown('<h1 class="title-class">An AI-Powered YouTube Video Assistant</h1>', unsafe_allow_html=True)

    st.write("""
        VidSage is a RAG-based architecture that transforms YouTube videos into interactive knowledge sources.
        \nBy providing a YouTube video ID, VidSage generates a complete transcript, a text summary and allows users to ask detailed questions about the video's content.
        \nUse the sidebar to navigate between the 'Add Video', 'AI Assistant' and 'Video Insights' options, or come back to this home page anytime.
        \nThere will be more features to come, feel free to drop in suggestions and feedback.
        If you like this project please don't forget to star the [GitHub repo](https://github.com/quickSilverShanks/VidSage/).
    """)



# Run the app
# if __name__ == '__main__':
#     main()

show_home_page()
