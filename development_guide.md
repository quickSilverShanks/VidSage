## Steps followed in project development



### Setting up project

* Create the new project in Guthub
* Pull the project in local machine & check repo info to confirm
```shell
git clone git@github.com:quickSilverShanks/VidSage.git
cd VidSage
git remote -v
git branch
```
* Create new virtual environment using miniconda powershell prompt
```shell
conda create -n vidsage python=3.11
conda activate vidsage
conda env list
```

* Install required packages for notebook experiments (use miniconda)
```shell
pip install youtube-transcript-api pandas openai tqdm elasticsearch matplotlib sentence-transformers transformers
pip freeze > requirements.txt
```



### Notebook Experiments

**Data Preparation:** This notebook contains experimental codes to transcript videos, chunk input transcript, clean text and generate summary & keywords. This notebook also contains codes for ElasticSearch text and hybrid search based retrieval operations coupled with a basic rag pipeline following aforementioned steps.

Run `Ollama` in docker and use `phi3`(if ram>=6GB or GPU>=4GB) or `gemma2:2b` to clean and summarize the text. The downloaded model can be tested with ollama terminal command `ollama run gemma2:2b`.
```shell
docker run -it \
    -v ollama:/root/.ollama \
    -p 11434:11434 \
    --name ollama \
    ollama/ollama
```
```shell
docker exec -it ollama bash
ollama pull gemma2:2b
```

> Note: Gemma2:2b has a context length of ~8000 so try not to exceed 5000 words, could cause to drop the input text from prompts. Use `phi3` for better responses and use `gemma2:2b` for fast responses. Its suggested to use phi3 to generate summarized chunks so that RAG will have better contexts to use to generate replies. However, upon multiple runs it was also observed that phi3 generated random gibberish instead of summary for most of the text blocks, worth looking into in future modifications.

In the later parts of same notebook, sentence embedding and ElasticSearch indexing is being done. This requires running `ElasticSearch` in docker with below terminal command. Once it starts running, ES cluster information can be checked with terminal command `curl localhost:9200`.
```shell
docker run -it \
--rm \
--name elasticsearch \
-p 9200:9200 \
-p 9300:9300 \
-e "discovery.type=single-node" \
-e "xpack.security.enabled=false" \
docker.elastic.co/elasticsearch/elasticsearch:8.4.3
```

**Docker Compose:** Above both docker services can be run at once with below  `docker-compose.yaml` content. Use terminal command `docker compose up -d` from the directory containing this file.
```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.4.3
    ports:
      - "9200:9200"
      - "9300:9300"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false

  ollama:
    image: ollama/ollama
    volumes:
      - ./ollama:/root/.ollama  # Mount your local .ollama directory for configuration; feel free to change local folder
    ports:
      - "11434:11434"
```

> Note: Running both of these docker services drained my 8GB RAM completely which only had limited free ram available with other applications running. So, I switched to using GPU to run ollama model. This modified compose file can be run with command `docker compose -f docker-compose-gpu.yml up -d`.

Below command can be used to check the existing list of index in ElasticSearch(vidsage-elasticsearch-1 is the name of ES container running from above docker compose command):
```shell
docker exec -it vidsage-elasticsearch-1 /bin/bash -c 'curl -X GET "localhost:9200/_cat/indices?v"'
```


<br><br><br><hr><hr>

### Side notes

Useful Reference Links:
* Sample Project: https://github.com/AudhootChavan/llm_zc_2024_project_audhoot_chavan_parlamind/blob/main/README.md
* Video Transcripts Generation: https://www.geeksforgeeks.org/python-downloading-captions-from-youtube/
* Ready to Use Transcript Data: https://huggingface.co/datasets/PleIAs/YouTube-Commons
* Mastering Summarization Techniques: A Practical Exploration with LLM - Martin Neznal: https://youtu.be/Uoc1k6xdbEg?si=YxAjgjnkTxIRUCz7

Useful Tips:
* To check how much space is being used by docker, use command  `docker system df -v`.
* To check how much ram/resources are being used by docker services/containers, use command `docker stats`.
