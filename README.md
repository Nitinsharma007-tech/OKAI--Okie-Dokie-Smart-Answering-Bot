#  OKAI - Okie Dokie Smart Answering Bot

> **An AI-Powered ERP Assistant built using Retrieval-Augmented Generation (RAG), Semantic Search, and Google Gemini AI.**

---

## 📌 Overview

OKAI is an intelligent ERP chatbot designed to answer user queries from ERP training material in natural language.

Unlike traditional keyword-based chatbots, OKAI understands the **meaning (intent)** behind a question using **Semantic Search** and retrieves the most relevant ERP knowledge before generating an accurate response using **Google Gemini AI**.

Whether users ask the same question in different ways, OKAI is capable of retrieving the correct information and providing consistent answers.

---

## 🚀 Features

- 🧠 Semantic Search using Sentence Transformers
- 📚 Retrieval-Augmented Generation (RAG)
- 🤖 Google Gemini AI Integration
- 📄 Automatic Context Building
- ⚡ Fast Knowledge Retrieval
- 💬 Natural Language Question Answering
- 🎯 Intent-Based Search (Not Keyword Search)
- 📊 Retrieved Knowledge Viewer
- 🎨 Interactive Streamlit Dashboard
- 🔄 Multi API-Key Support with Automatic Fallback
- 📁 Structured ERP Knowledge Base

---

## 🛠 Tech Stack

### AI & Machine Learning
- Google Gemini 2.5 Flash
- Sentence Transformers
- all-MiniLM-L6-v2

### Backend
- Python
- NumPy
- JSON

### Frontend
- Streamlit
- HTML
- CSS

### Search
- Semantic Search
- Vector Embeddings
- Cosine Similarity

---

## 🏗 Project Architecture

```
User Question
      │
      ▼
Semantic Search
      │
      ▼
Retrieve Top Relevant Knowledge
      │
      ▼
Context Builder
      │
      ▼
Gemini AI
      │
      ▼
Final ERP Answer
```

---

## 📂 Project Structure

```
OKAI/
│
├── app/
│   ├── chatbot.py
│   ├── gemini_agent.py
│   ├── semantic_search.py
│   ├── context_builder.py
│   ├── embedding_generator.py
│   ├── transcript_cleaner.py
│   └── ...
│
├── data/
│   ├── cleaned_transcripts/
│   ├── embeddings/
│   └── knowledge_base/
│
├── master_data/
│
├── main_chatbot.py
├── main_semantic.py
├── main_context.py
├── requirements.txt
└── README.md
```

---

## 💡 How It Works

1. User asks a question.
2. Question is converted into an embedding.
3. Semantic Search finds the most relevant ERP topics.
4. Context Builder prepares the retrieved knowledge.
5. Gemini AI generates a response only from the retrieved context.
6. Final answer is displayed along with retrieved knowledge.

---

## 🎯 Example

### User Query

> How can I prepare a timetable?

### Another User Query

> What is the process of creating a timetable?

### Another User Query

> Steps for making a timetable?

### Result

✅ Same intent detected

✅ Same ERP knowledge retrieved

✅ Accurate answer generated

---

## 📸 Demo

### Current Features

- Semantic Search
- RAG Pipeline
- Gemini AI Integration
- Streamlit Dashboard
- ERP Knowledge Retrieval
- Intent Recognition
- Multiple Question Variations Support

---

## ⚙ Installation

Clone the repository

```bash
git clone https://github.com/Nitinsharma007-tech/OKAI--Okie-Dokie-Smart-Answering-Bot.git
```

Go inside project

```bash
cd OKAI--Okie-Dokie-Smart-Answering-Bot
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate

### Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
GEMINI_API_KEY_1=YOUR_KEY
GEMINI_API_KEY_2=YOUR_KEY
GEMINI_API_KEY_3=YOUR_KEY
```

Run the project

```bash
streamlit run main_chatbot.py
```

---

## 📈 Future Improvements

- Authentication System
- Conversation Memory
- Voice-based ERP Assistant
- Image & Document Understanding
- Better UI/UX
- Faster Vector Database
- Deployment on Streamlit Cloud
- Analytics Dashboard
- Flowchart Generation
- ERP Video Reference Linking

---

## 👨‍💻 Contributors

- **Nitin Sharma** – AI & Data Science Developer
- **Vidish** – AI Developer
- **Yuvneet Sapra** – Backend & Integration

---

## ⭐ Project Highlights

- Intent-Based Semantic Search
- RAG Architecture
- Gemini AI Powered
- Multiple API Key Support
- Modular Codebase
- Streamlit Interactive UI
- Optimized for ERP Knowledge Retrieval

---

## 📜 License

This project is developed for educational and research purposes.

---

<<<<<<< HEAD
# ⭐ If you like this project, don't forget to Star the repository!
=======
# ⭐ If you like this project, don't forget to Star the repository!
>>>>>>> 8969619 (Added clickable suggested questions support)
