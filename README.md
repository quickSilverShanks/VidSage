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

<details>
  <summary><b>TODO List</b></summary>

- [x] Notebook Experiment: Data Preparation(Transcription, Cleaning & Summarization)
- [x] Notebook Experiment: Data Preparation(Chunking, Embedding & ElasticSearch Indexing)
- [x] Notebook Experiment: Basic RAG pipeline (Search - Text|Vector|Hybrid)
- [ ] Notebook Experiment: Generate Gold Standard Data
- [ ] Notebook Experiment: Evaluate Retrieval and RAG Flow (Add Hyperopt based optimization parameters)
- [ ] Prefect: Data Ingestion Pipeline
- [ ] Flask: Retrieval API
- [x] RAG Pipeline in Python Scripts
- [x] StreamLit: Application UI
- [x] Docker: Containerize
- [ ] Portgres: Logging
- [ ] Grafana: Reporting and User Feedback
- [ ] Additional Features: Query Restructure
- [ ] Additional Features: Document Reranking
- [ ] Additional Features: Video Insights
- [ ] Additional Features: Evaluation and Optimization of Summarization process
- [x] Add Documentation

</details>


> [!NOTE]
> **Current Status**: The project can be run in at-least 3 possible ways(recommended to go with last option which is the full build of this application):
> * `CLI Mode: Using Scripts`: This allows user to get the results in terminal with just a few scripts. User can download any video transcript through scripts and ask any query related to that video. But since this runs in local, it requires you to install required python libraries.
> * `Streamlit UI: CPU/GPU with minimal docker setup`: This is recommended if you intend to make your own modifications to the application. This option also requires user to install packages in local machine but runs with minimal docker services and has Streamlit UI as well. You can actively make changes to UI and refresh the page to see its effect.
> * `Streamlit UI: CPU/GPU with complete docker setup`: This is recommended for end-users who wants to use the full functionality with all the docker services running and packages installed in docker container. Once the container has been set up, it can be used with ease the next time. Its just like installing an application and then using it whenever you want 😉

**Next Planned Updates**: Adding DB support and User Feedback | Evaluating and Optimizing Retrieval | Prefect data Ingest Pipeline

Check `development_guide.md` for a detailed documentation of experiments and steps taken to develop this project.

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
python ./scripts/get_transcript.py --video_id zjkBMFhNj_g --index_name video-transcripts-vect --filepath ./data/summary_transcripts
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



## StreamLit Application UI

The .env file can be used to configure/modify the default behaviour of application UI:
```bash
# [LLM]
OPENAI_API_KEY =  "ollama"
OPENAI_API_URL = 'http://vidsage-ollama:11434/v1/'
LLM_MODEL = 'gemma2:2b'

# [ElasticSearch]
ELASTICSEARCH_URL = "http://vidsage-elasticsearch:9200"
ES_INDEX = "video-transcripts-app"

# [Sentence Embedding]
VECTOR_MODEL = 'multi-qa-MiniLM-L6-cos-v1'
VECTOR_DIMS = 384

# [YouTube Transcript Config]
LANG = ['en', 'en-US', ]

# [PostGreSQL]
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "dbpass"
DB_HOST = "postgres_db"
DB_PORT = "5432"
```

The streamlit application has following pages:
* Home: Landing page of application with default url http://localhost:8501/. Displays initialization status in the sidebar when opened/reloaded.
* Add Video: Provides functionality to add a new video user-requested transcript in the ElasticSearch index.
* AI Assistant: RAG Chatbot for user to query any indexed video.


## Running the Application

Before running the application make sure you have `docker`, `docker-compose`(optional) and `git cli` installed in your machine. Its recommended to have 16GB CPU RAM and 4GB GPU but the application has also been successfully tested on 8GB CPU RAM (just that its really slow and might require you to close other running apps to free up some RAM).

Please note, internet connection would be required to download the services(like ElasticSearch, Ollama etc), models(llms like gemma2:2b, sentence transformers etc) and video transcripts. Querying the RAG assistant does not require internet since the llm will be downloaded and used from local.

### CLI Mode: Using Scripts

**Ideal Scenario**: For running experiments and testing out RAG framework without going into UI. Requires installing python libraries in a virtual environment.

* Download the project to local and go to the project folder 'VidSage'.
* Run elasticSearch and Ollama services with below command. If 'docker-compose' works on your installation, use it instead of 'docker compose'.
```shell
docker compose up -d                              # this uses cpu and ram to run the llm model
docker compose -f docker-compose-gpu.yml up -d    # this runs the llm model on gpu
```
* Check the name of ollama service with `docker ps` command, most probably it will be 'vidsage-ollama-1'. Run below command to pull the `gemma2:2b` model which will be used.
```shell
docker exec -it vidsage-ollama-1 bash ollama pull gemma2:2b
```
* Use miniconda(or any other tool) of your preference to create a new virtual environment, activate it and then install required libraries.
```shell
pip install -r requirements.txt
```
* Run below script to fetch and index the transcript(for instance, YQcuTYcxxWc). If the transcript is not available in specified filepath it will be downloaded and indexed.
```shell
python ./scripts/get_transcript.py --video_id YQcuTYcxxWc --index_name video-transcripts-vect --filepath ./data/summary_transcripts
```
* Run below scripts to ask your question.
```shell
python ./scripts/rag_assistant.py --index_name video-transcripts-vect --video_id YQcuTYcxxWc --query "Who was socrates?"
```

### Streamlit UI: CPU/GPU with minimal docker setup

**Ideal Scenario**: For easy development of UI and testing out available features of application without building app's docker container. Requires installing python libraries in a virtual environment.

If you don't want to use the full build application with all the services in docker, this method allows you to quickly start ES and Ollama services and get started with Streamlit UI. Follow the steps below.

* Download the project to local and go to the project folder 'VidSage'.
* Run elasticSearch and Ollama services with below command. If 'docker-compose' works on your installation, use it instead of 'docker compose'.
```shell
docker compose up -d                              # this uses cpu and ram to run the llm model
docker compose -f docker-compose-gpu.yml up -d    # this runs the llm model on gpu
```
* Check the name of ollama service with `docker ps` command, most probably it will be 'vidsage-ollama-1'. Run below command to pull the `gemma2:2b` model which will be used.
```shell
docker exec -it vidsage-ollama-1 bash ollama pull gemma2:2b
```
* Use miniconda(or any other tool) of ytour preference to craete a new virtual environment, activate it and then install required libraries.
```shell
pip install -r requirements.txt
```
* Open the 3 codes 'vidsage_ui.py', 'add_video.py' and 'ai_assistant.py'. In all of these codes uncomment the one line that imports "utils.init_app_local" and comment the other one line that imports "utils.init_app". This ensures that you don't try to import the variables .env file which won't be available in local.
* Go to the 'app' folder in terminal. Start the streamlit service with below command.
```shell
streamlit run vidsage_ui.py
```
* Once started it will show the url in terminal. Go to the url http://localhost:8501/ to view homepage of this application. Wait for the page to open, might take 10-20 seconds.
* On the left sidebar of homepage it will show a spinner with text "Initializing Application...". Once its done in 30-40 seconds, it will turn green with text "Ready...". Now you can use the application features.
* Go to `AI Assistant` page where some video ids are already available to which you can ask your query. It takes 10-30 seconds to get the reply, depends on resources (duh!).
* If you want to use any other video to query and its not available in drop-down, go to `Add Video` page. Put in the video id and click on Fetch button.
> Depending on the length of video this is going to take considerable amount of time so if you're just testing out the application I would `recommend using a nice informative video with length 10-15 minutes`.
* Once the video transcript has been fetched(and indexed), it can be queried from "AI Assistant" page.

### Streamlit UI: CPU/GPU with complete docker setup

**Ideal Scenario**: For end-users of this application. Containerized application with all features enabled to use.

This is the recommended way to use this application. All the services will be built inside a docker comtainer and its going to take 15-20 minutes depending on internet speed and hardware. This is just like installing an application, one its done you can launch and use it next time within just a few seconds. Plus, no library gets installed in local, its all in docker land, so enjoy! :smiley:

**Why 15-20 minutes?** On its first run it will download images for all the required services as mentioned in `docker-compose-app.yml` file and then download the llm model and sentence transformer model specified in `.env` file. It also installs the packages mentioned in `requirements.txt` and indexes available video transcripts in 'app_data' folder.

* Download the project to local and go to the project folder 'VidSage'.
* Run docker compose with below command. If 'docker-compose' works on your installation, use it instead of 'docker compose'.
```shell
docker compose -f docker-compose-app.yml up -d
```
* It takes 15-20 minutes to build the docker container. Grab a cup of tea, watch an episode of The Big Bang Theory and when you come back, open url http://localhost:8501/ to access the Streamlit UI. :relaxed:
* Demo Video of application yet to be uploaded.



<br><br><br><br>
<hr>

<div align="center">
If you like this project, please consider giving it a ⭐️ **star** to help others discover it. 

[![GitHub Stars](https://img.shields.io/github/stars/quickSilverShanks/VidSage.svg?style=social)](https://github.com/quickSilverShanks/VidSage/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/quickSilverShanks/VidSage.svg?style=social)](https://github.com/quickSilverShanks/VidSage/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/quickSilverShanks/VidSage.svg)](https://github.com/quickSilverShanks/VidSage/issues)
</div>
Please note this is not open for contributions yet as basic features are still being added in, but feel free to 🍴 **fork** it and explore the code!
