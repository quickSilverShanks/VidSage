# VidSage: AI-Powered YouTube Video Assistant

<div align="center">
  <img src="https://github.com/user-attachments/assets/0c964ebf-8170-4a55-a8bc-0983925f7df5" alt="vidsage_mod1" width="600"/>
</div>

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

- [x] Notebook Experiment: Data Preparation(Transcription, Cleaning & Summarization)
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
- [ ] Additional Features: Evaluation and Optimization of Summarization process
- [ ] Add Documentation



## Data Preparation

Use the script `generate_smry.py` to generate and save pickle files with uid, original video transcript and summarized text columns. For a given video_id, run the script with below terminal command
```shell
python generate_smry.py --vid zjkBMFhNj_g --dest ./data/summary_transcripts
```
> The column 'uid' is created by appending video_id, block_id and start_time separated by '__' so that it can be extracted later on if needed.

Rather than running this script multiple times, prepare a single csv file with 20 video ids(or any preferred number) and run the script `generate_allsmry.py` with below command to get all the summaries for all 20 videos in a single pickle file. This will generate the combined pickle file `allsmry.pkl`.
```shell
python generate_allsmry.py --inp vidsource.csv --dest ./data/summary_transcripts
```
