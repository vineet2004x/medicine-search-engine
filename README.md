# AI Medicine Search Application

A simple, lightweight API demonstrating **Semantic Search** and **Fuzzy Spelling Correction** on a medical dataset using Python and FastAPI.

## Table of Contents
1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Setup & Installation](#setup--installation)
5. [Running the Application](#running-the-application)
6. [API Endpoints & Usage](#api-endpoints--usage)
7. [How It Works](#how-it-works)

---

## Overview

This application demonstrates how to build a semantic search tool *without* complex external dependencies like heavy vector databases or Large Language Models (LLMs). It caches sentence embeddings in memory and calculates similarities locally, making it extremely fast, portable, and ideal for smaller datasets.

---

## Technology Stack

* **Python 3.10+**
* **FastAPI**: Fast, asynchronous web framework for building APIs.
* **SQLite**: Lightweight disk-based relational database.
* **SQLAlchemy**: Python SQL toolkit and Object-Relational Mapper (ORM).
* **Sentence Transformers**: Pre-trained model (`all-MiniLM-L6-v2`) to generate 384-dimensional text embeddings.
* **RapidFuzz**: Fast string matching for spelling correction.
* **scikit-learn**: Used for computing cosine similarity between query embeddings and cached medicine embeddings.

---

## Architecture

The project follows a clean, modular structure:

* `database.py`: Database connection settings, SQLAlchemy models, and initial seeding of sample data.
* `embeddings.py`: Generates semantic text embeddings and caches them in memory.
* `fuzzy_match.py`: Spelling correction utility that replaces misspelled medicine names in user queries.
* `search.py`: Core search pipeline that orchestrates the spelling correction, query embedding, and cosine similarity comparison.
* `app.py`: FastAPI application routing, lifespan startup handler, and endpoints.

---

## Setup & Installation

Follow these steps to set up and run the application locally.

### 1. Set Up a Virtual Environment (Optional but recommended)
```bash
python -m venv .venv
# Activate on Windows:
.venv\Scripts\activate
# Activate on macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy sentence-transformers rapidfuzz scikit-learn
```

---

## Running the Application

Start the FastAPI application using `uvicorn`:

```bash
uvicorn app:app --reload
```

Once running, the API will be available at `http://127.0.0.1:8000`. You can access the interactive Swagger documentation at `http://127.0.0.1:8000/docs`.

On startup, the app automatically:
1. Creates the SQLite database file `medicines.db` if it doesn't exist.
2. Seeds it with a list of sample medicines (Paracetamol, Ibuprofen, Amoxicillin, Cetirizine, Metformin, Atorvastatin, Omeprazole).
3. Pre-calculates vector embeddings for all medicines and stores them in memory.

---

## API Endpoints & Usage

### 1. Retrieve All Medicines
* **Endpoint**: `GET /medicines`
* **Description**: Fetches all medicine records in the database.
* **Example curl**:
  ```bash
  curl -X GET http://127.0.0.1:8000/medicines
  ```

### 2. Regenerate Embeddings
* **Endpoint**: `POST /generate_embeddings`
* **Description**: Explicitly reloads the database and updates the in-memory cache of embeddings.
* **Example curl**:
  ```bash
  curl -X POST http://127.0.0.1:8000/generate_embeddings
  ```

### 3. Search Medicines
* **Endpoint**: `POST /search`
* **Description**: Performs a hybrid fuzzy + semantic search.
* **Request Body**:
  ```json
  {
    "query": "<your search query>"
  }
  ```

#### Example 1: Typo Correction
* **Query**: `{"query": "pracetamul"}` (spelled Paracetamol incorrectly)
* **Example curl**:
  ```bash
  curl -X POST http://127.0.0.1:8000/search \
       -H "Content-Type: application/json" \
       -d "{\"query\": \"pracetamul\"}"
  ```
* **Response**:
  ```json
  {
    "MatchedMedicine": "Paracetamol",
    "GenericSalt": "Acetaminophen",
    "Uses": "Fever reduction, relief of mild to moderate pain (headache, muscle ache, toothache).",
    "Dosage": "500mg",
    "Frequency": "Every 4 to 6 hours as needed. Maximum 4000mg per day.",
    "SideEffects": "Nausea, skin rash, liver damage if taken in high doses.",
    "SimilarityScore": 0.9423,
    "CorrectedQuery": "Paracetamol"
  }
  ```

#### Example 2: Semantic search for symptoms / uses
* **Query**: `{"query": "something for stomach acid and GERD"}`
* **Example curl**:
  ```bash
  curl -X POST http://127.0.0.1:8000/search \
       -H "Content-Type: application/json" \
       -d "{\"query\": \"something for stomach acid and GERD\"}"
  ```
* **Response**:
  ```json
  {
    "MatchedMedicine": "Omeprazole",
    "GenericSalt": "Omeprazole",
    "Uses": "Treatment of gastroesophageal reflux disease (GERD), heartburn, stomach ulcers, and damage to the esophagus caused by stomach acid.",
    "Dosage": "20mg",
    "Frequency": "Once daily in the morning, 30 to 60 minutes before breakfast.",
    "SideEffects": "Headache, stomach pain, gas, nausea, diarrhea.",
    "SimilarityScore": 0.5841,
    "CorrectedQuery": "something for stomach acid and GERD"
  }
  ```

---

## How It Works

1. **Text Document Creation**: 
   Every medicine row is formatted into a text document block representing its properties:
   `"Medicine: <Name>. Generic Salt: <Salt>. Uses: <Uses>. Dosage: <Dosage>..."`
2. **Embedding Generation**: 
   The SentenceTransformer model `all-MiniLM-L6-v2` encodes each document block into a 384-dimensional dense vector representing the semantic meaning.
3. **Fuzzy Spelling Correction**: 
   When a search is requested, the query is parsed. Words that resemble medicine names (e.g. `pracetamul` -> `Paracetamol`) are corrected using RapidFuzz matching against database names.
4. **Similarity Comparison**: 
   The corrected query is embedded, and `scikit-learn` computes its Cosine Similarity against all cached medicine embeddings. The best match is returned.
