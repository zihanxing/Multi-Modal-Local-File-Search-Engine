# Project: Local File Search Engine with Advanced Capabilities

## Table of Contents
1. Introduction
2. Supported File Types
3. Core Features
4. Technology Stack
5. Privacy Focus
6. Benefits
7. Data Pipeline
8. Modeling Approach
9. Model Evaluation Approach
10. Previous Approaches and Novelty
11. Performance Analysis
12. Deep Learning vs Non-Deep Learning Approach
13. Comparison to a Naive Approach

## Introduction
The goal of this project is to develop a privacy-focused local search engine for efficiently finding files on your laptop. This includes images (photos), videos, documents (PDFs, DOCx, PPTs, etc.), and audio files.

### Supported File Types
1. Images (Photos)
2. Videos
3. Documents (PDFs, DOCx, PPTs, etc.)
4. Audio files

## Core Features
Automatic Indexing: New files are automatically indexed upon upload for quick retrieval.
Keyword Search: Search for files using keywords in their names or metadata.
Semantic Search: Leverage AI to understand file content and deliver more relevant results.
Image Search: Find similar images by uploading a reference image.

## Technology Stack
Image Similarity Search: OpenCLIP
Video Analysis: Video CLIP models or alternative solutions.
Document Understanding: BERT, OpenAI
Audio Analysis: to do

## Benefits
Efficiency: Quickly find the files you need, even with large amounts of data.
Privacy Focus: Maintain complete control over your data. All processing occurs locally on the user’s laptop. No data is sent to external servers, ensuring complete privacy.
Advanced Search: Go beyond simple keyword searches and find files based on their content.
Versatility: Search across various file types, including images, videos, documents, and audio.

## Data Pipeline
The data pipeline involves loading local files, embedding all the files, and putting them into the vector database.

## Modeling Approach
The modeling approach involves calculating similarity scores between query and files embeddings.

## Model Evaluation Approach
The model evaluation approach will be detailed in the upcoming sections.

## Previous Approaches and Novelty
This project is novel in its local, open-sourced, and LLM-powered-recommendation approach. Previous approaches and their comparison will be detailed in the upcoming sections.

## Performance Analysis
The performance of the model will be analyzed relative to previous approaches. The similarity calculation metric will be detailed in the upcoming sections.

## Deep Learning vs Non-Deep Learning Approach
The deep learning approach involves using embedding models. The non-deep learning approach involves using TFIDF (only for text).

## Comparison to a Naive Approach
The naive approach involves a keyword search without embeddings of files. The comparison will be detailed in the upcoming sections.