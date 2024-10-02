# VidSage: AI-Powered YouTube Video Assistant

VidSage is a RAG-based architecture that transforms YouTube videos into interactive knowledge sources. By providing a YouTube video ID, VidSage generates a complete transcript, a text summary and allows users to ask detailed questions about the video's content.
It integrates Elasticsearch with the RAG architecture to allow efficient retrieval of video information, especially for querying specific sections of the transcript.

**Key Features:**

* 📝 Automated Transcription: Generate and store YouTube video transcripts with accurate timestamps.
* 🔍 Interactive Q&A: Ask questions and get AI-powered answers based on the video content.
* 📊 Efficient Search: Leveraging Elasticsearch for fast and precise transcript retrieval.
* 📋 Comprehensive Summaries: Generate detailed video summaries with topic headings and descriptions.

VidSage simplifies knowledge extraction from video content, making it an invaluable tool for learning, research, and content analysis.

> Note: This project is in active development phase, feel free to drop in suggestions and feedbacks. More features and interactivity will be added in once MVP has been achieved.

## Workflow

- [ ] Notebook Experiment: Data Preparation(Transcription & Cleaning)
- [ ] Notebook Experiment: Data Preparation(Summarization)
- [ ] Notebook Experiment: Data Preparation(Chunking, Embedding & ElasticSearch Indexing)
- [ ] Notebook Experiment: Basic RAG pipeline (Search - Text|Vector|Hybrid)
- [ ] Notebook Experiment: Generate Gold Standard Data
- [ ] Notebook Experiment: Evaluate Retrieval and RAG Flow (Add Hyperopt based optimization parameters)
- [ ] AirFlow: Data Ingestion Pipeline
- [ ] Flask: Retrieval API
- [ ] StreamLit: Application UI
- [ ] Docker: Containerize
- [ ] Portgres: Logging
- [ ] Grafana: Reporting and User Feedback
- [ ] Additional Features: Query Restructure
- [ ] Additional Features: Document Reranking
- [ ] Additional Features: Video Insights
- [ ] Add Documentation
