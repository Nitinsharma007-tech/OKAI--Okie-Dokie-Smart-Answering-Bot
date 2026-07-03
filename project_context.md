# 🤖 OKAI — Project Context & Developer Guide

> This document explains the complete architecture, workflow, data pipeline, folder structure, AI pipeline, deployment process, and future roadmap of the OKAI ERP Assistant.

---

# 📌 Project Overview

OKAI (Okie Dokie Smart Answering Bot) is an AI-powered ERP Assistant built using Retrieval-Augmented Generation (RAG).

Unlike traditional keyword-based chatbots, OKAI understands the **intent (meaning)** behind a user's question and retrieves the most relevant ERP knowledge before generating a response using Google Gemini.

Example

User 1:

> How do I collect student fees?

User 2:

> What is the procedure for fee collection?

User 3:

> Steps to collect fees

All three questions represent the same intent.

OKAI retrieves the same ERP knowledge and produces the same answer.

---

# 🎯 Objective

The goal of OKAI is to answer ERP-related questions accurately using internal ERP training knowledge instead of generating information from general AI knowledge.

The chatbot must:

- Understand intent
- Retrieve correct ERP topic
- Build context
- Generate accurate answer
- Never hallucinate

---

# 🏗 Overall Architecture

```

User
│
▼
Streamlit UI
│
▼
User Question
│
▼
Semantic Search
│
▼
Top-K Relevant Topics
│
▼
Context Builder
│
▼
Gemini Prompt
│
▼
Gemini AI
│
▼
Final Answer
│
▼
Display Retrieved Knowledge

```

---

# 🧠 AI Pipeline

The project follows a Retrieval-Augmented Generation (RAG) architecture.

```

Training Videos
│
▼
Transcript Generation
│
▼
Transcript Cleaning
│
▼
Knowledge Extraction
│
▼
Knowledge JSON
│
▼
Embedding Generation
│
▼
Semantic Search
│
▼
Context Builder
│
▼
Gemini AI
│
▼
Final Response

```

---

# 📂 Data Pipeline

## Step 1

Training videos are collected.

These videos explain ERP modules such as:

- Academics
- Fee
- Payroll
- Transport
- Inventory

---

## Step 2

Transcripts are generated.

File

```

main_transcript.py

```

Output

```

Raw Transcript

```

---

## Step 3

Transcript Cleaning

Purpose

- Remove timestamps
- Remove unwanted characters
- Remove duplicate lines
- Remove filler words

File

```

main_cleaner.py

```

Output

```

Clean Transcript

```

---

## Step 4

Knowledge Extraction

Gemini converts transcript into structured knowledge.

Output example

```json
{
  "topic": "...",
  "summary": "...",
  "steps": [],
  "navigation": [],
  "keywords": []
}
```

File

```

main_knowledge.py

```

---

## Step 5

Master Knowledge

All extracted topics are merged.

File

```

main_master_knowledge.py

```

Output

```

master_knowledge.json

```

---

## Step 6

Embedding Generation

Each topic is converted into a vector embedding.

Model

```

all-MiniLM-L6-v2

```

Output

```

embeddings.npy

```

File

```

main_embeddings.py

```

---

## Step 7

Semantic Search

User question is converted into an embedding.

Cosine Similarity is calculated.

Top K matches are retrieved.

Current

```

Top K = 3

```

File

```

semantic_search.py

```

---

## Step 8

Context Builder

Retrieved topics are merged into a clean context.

Purpose

- Remove duplication
- Preserve steps
- Preserve navigation
- Prepare Gemini prompt

File

```

context_builder.py

```

---

## Step 9

Gemini AI

Prompt

```

Question
+
Retrieved Context

```

Gemini generates an answer ONLY using retrieved ERP knowledge.

No hallucination allowed.

---

# 📁 Folder Structure

```

OKAI/

│

├── app/

│ ├── chatbot.py

│ ├── gemini_agent.py

│ ├── semantic_search.py

│ ├── context_builder.py

│ ├── transcript.py

│ ├── cleaner.py

│ ├── embedding_generator.py

│ ├── knowledge_builder.py

│ └── ...

│

├── data/

│ ├── transcripts/

│ ├── cleaned/

│ ├── embeddings/

│ ├── knowledge/

│

├── master_data/

│

├── main_chatbot.py

├── main_cleaner.py

├── main_transcript.py

├── main_knowledge.py

├── main_master_knowledge.py

├── main_embeddings.py

├── README.md

├── PROJECT_CONTEXT.md

└── requirements.txt

```

---

# 💬 Chatbot Workflow

```

User asks question

↓

Semantic Search

↓

Top 3 Topics

↓

Context Builder

↓

Gemini

↓

Final Answer

↓

Retrieved Knowledge

```

---

# 🚀 Current Features

✅ Semantic Search

✅ RAG

✅ Google Gemini

✅ Streamlit UI

✅ Suggested Questions

✅ Top-3 Retrieval

✅ Multiple Gemini API Keys

✅ API Rotation

✅ Knowledge Viewer

✅ Modern UI

---

# ⚠ Current Limitations

- Response depends on Gemini API quota
- Retrieval quality can be improved
- No streaming response yet
- No conversation memory
- No authentication
- No vector database
- Uses local embeddings

---

# 🎯 Future Roadmap

## Phase 1

- Better UI
- Better UX
- Loading animations
- Streaming responses
- Better cards

---

## Phase 2

- FAISS
- Better ranking
- Hybrid Search
- Metadata Filtering

---

## Phase 3

- Authentication
- Multi-user support
- Conversation History
- Chat Export
- Voice Input

---

## Phase 4

- Flowchart Generation
- ERP Screenshots
- Image Understanding
- PDF Understanding

---

## Phase 5

- Production Deployment
- Docker
- Railway
- AWS
- Azure

---

# 🛠 Tech Stack

Frontend

- Streamlit

Backend

- Python

AI

- Google Gemini
- Sentence Transformers

ML

- PyTorch

Search

- Semantic Search

Embedding Model

- all-MiniLM-L6-v2

Vector Search

- Cosine Similarity

Deployment

- Railway

Version Control

- Git
- GitHub

---

# 💡 Development Principles

Every new feature should follow these rules:

- Never break existing functionality.
- Keep modules independent.
- Use reusable functions.
- Write clean code.
- Maintain folder structure.
- Document every major feature.
- Avoid hardcoded paths.
- Use environment variables for secrets.

---

# 👥 Contributors

- **Nitin Sharma** — AI & Data Science, RAG Pipeline, Streamlit UI, Semantic Search
- **Vidish** — Development & Integration
- **Yuvneet Sapra** — Development & Integration

---

# 📅 Project Timeline

### Phase 1
- Built transcript extraction pipeline
- Cleaned ERP transcripts
- Generated structured knowledge

### Phase 2
- Built embedding pipeline
- Implemented semantic search
- Developed context builder

### Phase 3
- Integrated Google Gemini
- Built RAG chatbot
- Developed Streamlit interface

### Phase 4
- Added multiple API key rotation
- Improved UI
- Railway deployment
- Future production optimization

---

# 📌 Notes

This document should always be updated whenever:

- New modules are added
- Pipeline changes
- Folder structure changes
- Deployment changes
- Major UI improvements
- New AI features
- New retrieval strategy
- New embedding model

Keeping this document up to date ensures every contributor understands the project architecture and development workflow.