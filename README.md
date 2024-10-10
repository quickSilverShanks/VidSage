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
- [x] Notebook Experiment: Data Preparation(Chunking, Embedding & ElasticSearch Indexing)
- [x] Notebook Experiment: Basic RAG pipeline (Search - Text|Vector|Hybrid)
- [ ] Notebook Experiment: Generate Gold Standard Data
- [ ] Notebook Experiment: Evaluate Retrieval and RAG Flow (Add Hyperopt based optimization parameters)
- [ ] AirFlow: Data Ingestion Pipeline
- [ ] Flask: Retrieval API
- [ ] StreamLit: Application UI
- [x] Docker: Containerize
- [ ] Portgres: Logging
- [ ] Grafana: Reporting and User Feedback
- [ ] Additional Features: Query Restructure
- [ ] Additional Features: Document Reranking
- [ ] Additional Features: Video Insights
- [ ] Additional Features: Evaluation and Optimization of Summarization process
- [ ] Add Documentation



> Note: Check `development_guide.md` for a detailed documentation of experiments and steps taken to develop this project.



## Data Preparation, ElasticSearch Indexing and RAG

This section dexcribes how to use the scripts to prepare single/multi video transcript document, index it using ElasticSearch and use a hybrid(text+vector) retrieval to implement RAG pipeline. The codes used in development of these scripts can be seen in the notebook `data_preparation.ipynb` and more developmental details can be found in `development_guide.md`.

Download this repository in local. With project folder as the current directory, run docker compose before running the other scripts. One of the below commands can be used depending on availability of GPU in local machine.
```shell
docker compose up -d    # this uses cpu and ram to run the llm model
docker compose -f docker-compose-gpu.yml up -d    # this runs the llm model on gpu
```
> Depending on how the docker and docker-compose was installed, above command might require 'docker-compose' so give it a try as well.

Use the script `generate_smry.py` to generate and save transcript documents as json files with uid, original video transcript, summarized text and keywords columns. For a given video_id, run the script with below terminal command(make sure you're in the root folder)
```shell
!python ./scripts/get_transcript.py --video_id zjkBMFhNj_g --index_name video-transcripts-vect --filepath ./data/summary_transcripts
```
> The column 'uid' is created by appending video_id, block_id and start_time separated by '__' so that it can be extracted later on if needed.

Rather than running this script multiple times, prepare a single csv file with multiple video ids and run the script `get_multitranscript.py` with below command to get all the transcript documents in a single json file. This will generate the combined json file `multi_tscribe.json` in provided destination folder.
```shell
python ./scripts/get_multitranscript.py --inp ./data/vidsource.csv --dest ./data/summary_transcripts --index_name "video-transcripts-vect"
```

Once one or more video_ids have been indexed, run `get_indexed_vids.py` script to get a frequency count of number of chunks created/indexed in ElasticSearch.
```shell
python ./scripts/get_indexed_vids.py
```

Now that we have at-least a single video transcripted and indexed, run the `rag_assistant.py` script providing an input query, ElasticSearch index name and a target video_id to use for response.
```shell
python ./scripts/rag_assistant.py --index_name video-transcripts-vect --video_id zjkBMFhNj_g --query "What is Jailbreak in context of LLMs?"
```



### StreamLit Application UI

The .env file can be used to configure/modify the default behaviour of application UI:
```bash
# LLM
OPENAI_API_KEY =  "ollama"
LLM_MODEL = 'gemma2:2b'

# ElasticSearch
ELASTICSEARCH_URL = "http://elasticsearch_app:9200"
ES_INDEX = "video-transcripts-app"

# Sentence Embedding
VECTOR_MODEL = 'multi-qa-MiniLM-L6-cos-v1'
VECTOR_DIMS = 384

# YouTube Transcript Config
LANG = ['en', 'en-US', ]

# PostGreSQL
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "dbpass"
DB_HOST = "postgres_db"
DB_PORT = "5432"
```

