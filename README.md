# Multi-modal Local File Search & Recommendation Engine 

## Introduction
This project is a multi-modal local file search and recommendation engine. It solves the problem of unintelligent file search and recommendation in current search engines on various operating systems, like Windows, Mac, and Linux. 

For example, when you search for `my latest resume` in the search bar, the search engine will return all files with the name `resume` in the file name, but it will not return the file `my latest resume` if the file name is not `my_latest_resume`, and it will not retuen files `CV` or `curriculum vitae` even if they are the same file as `resume`. This project aims to solve this problem by using local runnable LLM model to recommend keywords based on user queries.

Also, if you want to search for images, audio, or video files, the current search engine will not be able to do that. This project will solve this problem by using multi-modal search and recommendation techniques.


## Features
- Multi-modal search: using [Weaviate](https://weaviate.io/) as the vector search engine, where we set ImageBind as the vectorizer for every file type, including text, image, audio, and video.
- Recommendation: using fine-tuned `TinyLlama-1.1B` model to recommend keywords based and structured data based on user queries.

## Repo Structure

## Repository Structure

The repository is organized as follows, with each directory in the repository serving a specific purpose:

- `Notebooks`: Contains python notebooks of experiments and specific parts of weaviate backend testing.
- `assets`: Contains assets for the project
- `create_collections`: Contains the code for creating collections for different modalities of data.
- `data`: Contains the data used in the project.
- `fine_tune`: Contains the fine-tuning code for the tinyllamma model.
- `image`: Contains the images used in the project.
- `inference`: Contains the inference code for tinyllamma.
- `scripts`: Contains additional scripts for the project.
- `app.py`: The main application file - launches streamlit application that interfaces with the dockerized weaviate container.
- `docker-compose.yml`: The Docker Compose file for setting up the project environment on Windows.
- `docker-compose_1.yml`: The Docker Compose file for setting up the project environment on Mac.
- `requirementsc.txt`: The requirements file for the project.
- `session_state.py`: A frontend helper script for app.py for managing session state in streamlit.

## Overall Architecture

![alt text](<image/overview.png>)

## How to use
1. Clone the repository
```bash
git clone https://github.com/zihanxing/Multi-Modal-Local-File-Search-Engine.git
```
2. Creat a virtual environment(using conda in this case) for the project
```bash
conda create -n searchengine
conda activate searchengine
```
3. Install the required packages
```bash
pip install -r requirements.txt
```
4. Compose the docker containers to start the Weaviate server. Use docker-compose.yml for windows, and docker-compose_1.yml for mac   
```bash
docker compose up -d
```
5. Run the streamlit app
```bash
streamlit run app.py
```

## Limitations
- Practical compute restrictions; GPU essentially required to match recommendation speed of traditional search

- Model can not process keywords it has not seen before (e.g. Huggingface) - small model does not have enough knowledge

- Ingestion is a required step as and when new data is added

## Future Work

- Improve the quality of fine-tuning data to improve recommendation quality, so that the model can recommend more accurate keywords.

- Implement a more efficient ingestion pipeline to automatically ingest new data.



