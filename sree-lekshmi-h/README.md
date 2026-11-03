# 🍳 RecipePilot – AI-Powered Recipe Assistant

<img width="944" height="482" alt="image" src="https://github.com/user-attachments/assets/e6b5ccfe-efe5-4777-b3d9-4fa4f65d6cf9" />

## Project Overview

RecipePilot is an AI-powered recipe assistant that helps users discover recipes, understand cooking instructions, organize personal recipes, and get cooking assistance through natural language conversations.

It combines recipe discovery through an external API with Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to provide an interactive cooking experience.

## Problem Statement

Deciding what to cook with the ingredients available at home can be challenging. Users often spend time searching multiple websites for suitable recipes, understanding cooking instructions, planning meals, and maintaining personal recipe collections.

Traditional recipe platforms mainly provide predefined recipes and limited interaction. They may not offer personalized conversational assistance or allow users to retrieve information from their own recipe documents.

RecipePilot addresses these challenges by bringing recipe discovery, AI-powered cooking assistance, personal recipe management, PDF-based question answering, meal planning, and shopping-list generation into one application.

---

## Features

### 1. Recipe Finder
- Search for recipes using available ingredients.
- Retrieve matching recipes using TheMealDB API.
- Explore available recipe information.

### 2. Recipe Details
- View recipe ingredients and quantities.
- Read cooking instructions.
- Explore individual recipes.

### 3. AI Cooking Assistant
- Ask cooking-related questions using natural language.
- Receive AI-generated cooking suggestions and explanations.
- Maintain conversation history during the session.

### 4. Personal Recipe Library
- Upload PDF documents containing recipes.
- Extract text from uploaded documents.
- Manage uploaded recipe documents.

### 5. PDF-Based Question Answering
- Retrieve relevant information from uploaded recipe PDFs.
- Use retrieved content as context for AI-generated answers.
- Ask questions about personal recipe documents using RAG.

### 6. AI Meal Planner
- Generate meal-planning suggestions using AI.

### 7. Shopping List
- Generate shopping lists based on meal-planning requirements.

---

## Architecture

RecipePilot follows a client-server architecture consisting of a Streamlit frontend and a FastAPI backend.
```mermaid
flowchart TD

    subgraph USER["User"]
        U["User<br/>RecipePilot"]
    end

    subgraph FE["Streamlit Frontend"]
        direction LR
        F1["Recipe Finder"]
        F2["Recipe Details"]
        F3["AI Cooking Assistant<br/>(chat history in session state)"]
        F4["Personal Recipe Library"]
        F5["AI Meal Planner"]
        F6["Shopping List"]
    end

    subgraph BE["FastAPI Backend"]
        direction TB
        API["API Endpoints / Routes<br/>(Pydantic request and response validation)"]
        subgraph SVC["Application Services"]
            direction LR
            S1["Recipe Search Service"]
            S2["Recipe Details Service"]
            S3["AI Assistant / Agent Logic"]
            S4["PDF Ingestion Service"]
            S5["PDF Retrieval Service<br/>(RAG)"]
            S6["Meal Planning Service"]
            S7["Shopping List Service"]
        end
        API --> SVC
    end

    subgraph RAPI["Recipe API"]
        MEALDB["TheMealDB API"]
    end

    subgraph PDFDB["PDF Processing and Vector Database"]
        direction TB
        PYMUPDF["PyMuPDF<br/>Text Extraction"]
        CHUNK["Text Chunking"]
        ST["Sentence Transformers<br/>all-MiniLM-L6-v2"]
        CHROMA[("ChromaDB<br/>Vector Store")]
        PYMUPDF -->|"extracted text"| CHUNK
        CHUNK -->|"text chunks"| ST
        ST -->|"embeddings + chunk text"| CHROMA
    end

    subgraph LLM["AI / LLM Services"]
        GROQ["Groq LLM<br/>openai/gpt-oss-20b"]
    end

    %% User to Frontend
    U -->|"uses"| FE

    %% Frontend to Backend
    FE -->|"HTTP requests"| API
    API -->|"HTTP responses (JSON)"| FE

    %% Workflow 1 and 2: Recipe Finder and Details (TheMealDB only)
    S1 -->|"search by ingredients"| MEALDB
    MEALDB -->|"matching recipes"| S1
    S2 -->|"lookup recipe by ID"| MEALDB
    MEALDB -->|"ingredients, quantities, instructions"| S2

    %% Workflow 3, 6, 7: Groq-based workflows
    S3 -->|"cooking question / prompt"| GROQ
    GROQ -->|"AI response"| S3
    S6 -->|"meal planning prompt"| GROQ
    GROQ -->|"meal suggestions"| S6
    S7 -->|"shopping list prompt"| GROQ
    GROQ -->|"generated list"| S7

    %% Workflow 4: PDF upload and ingestion
    S4 -->|"PDF upload"| PYMUPDF

    %% Workflow 5: PDF question answering (RAG)
    S5 -->|"question text"| ST
    ST -->|"question embedding"| CHROMA
    CHROMA -->|"retrieved chunks"| S5
    S5 -->|"question + retrieved PDF context"| GROQ
    GROQ -->|"grounded answer"| S5

    %% Styling
    classDef frontend fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    classDef backend fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    classDef ai fill:#fff3e0,stroke:#ef6c00,color:#e65100
    classDef recipe fill:#fce4ec,stroke:#c2185b,color:#880e4f
    classDef pdf fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    classDef user fill:#eceff1,stroke:#455a64,color:#263238

    class F1,F2,F3,F4,F5,F6 frontend
    class API,S1,S2,S3,S4,S5,S6,S7 backend
    class GROQ ai
    class MEALDB recipe
    class PYMUPDF,CHUNK,ST,CHROMA pdf
    class U user
```

### Frontend – Streamlit

The frontend provides the user interface for recipe searching, viewing recipe details, interacting with the AI assistant, uploading recipe documents, generating meal plans, and managing shopping lists.

### Backend – FastAPI

The backend handles API requests, application logic, communication with external services, and AI-related operations. Pydantic is used for request and response validation.

### AI Integration – Groq

Groq provides access to the Large Language Model used for conversational cooking assistance and other AI-powered features.

### Recipe Data – TheMealDB

TheMealDB API is integrated to retrieve recipe information based on ingredients provided by users.

### Retrieval-Augmented Generation (RAG)

The Recipe Library supports PDF uploads. PyMuPDF extracts text from uploaded documents. Sentence Transformers converts the extracted text into embeddings, which are stored in ChromaDB.

When a user asks a question about uploaded recipes, the system retrieves relevant information from the vector database and provides it as context to the LLM to generate an answer.

### Frontend and Backend Communication

The Streamlit frontend communicates with the FastAPI backend through HTTP requests. The backend processes the requests and returns responses to the frontend for display.

---
## 📁 Project Structure

```text
sree-lekshmi-h/
│
├── backend/
│   └── app/
│       ├── agents/
│       ├── api/
│       ├── schemas/
│       ├── services/
│       └── main.py
│
├── frontend/
│   ├── pages/
│   ├── app.py
│   ├── api_client.py
│   └── hero_slideshow.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

```
## Concept Breakdown

| Concept | Implementation in RecipePilot |
|---|---|
| API Integration | TheMealDB for recipe search and information |
| LLM Integration | Groq for AI-generated responses |
| Retrieval-Augmented Generation | Retrieving relevant information from uploaded recipe PDFs |
| Text Extraction | PyMuPDF for extracting text from PDFs |
| Text Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector Database | ChromaDB for storing and retrieving embeddings |
| Client-Server Architecture | Streamlit frontend communicating with FastAPI backend |
| Data Validation | Pydantic |

---

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| Backend | FastAPI |
| API Server | Uvicorn |
| LLM | Groq (`openai/gpt-oss-20b`) |
| Recipe API | TheMealDB |
| Embeddings | Sentence Transformers |
| Vector Database | ChromaDB |
| PDF Processing | PyMuPDF |
| Data Validation | Pydantic |
| HTTP Communication | HTTPX, Requests |
| Environment Configuration | Python-dotenv |

---

## Application Screenshots

The following screenshots demonstrate the main interfaces and features of RecipePilot.

### Home Page

<img width="944" height="482" alt="image" src="https://github.com/user-attachments/assets/358b20c1-f683-4c88-949b-ca21d1a91c1c" />

<img width="896" height="365" alt="image" src="https://github.com/user-attachments/assets/4347ab9d-1696-468a-a073-b9864a7e12fb" />


### Recipe Finder

<img width="780" height="479" alt="image" src="https://github.com/user-attachments/assets/903eec89-f65f-4f76-b51b-53dcc1c50f72" />



### Recipe Details

<img width="602" height="454" alt="image" src="https://github.com/user-attachments/assets/47e9f52a-b281-4b3e-8339-2ca5cceeaf3f" />


### AI Cooking Assistant

<img width="897" height="459" alt="image" src="https://github.com/user-attachments/assets/d2aaf9b6-c5ae-4327-aaa5-ce8a1694570e" />


### Recipe Library

<img width="928" height="488" alt="image" src="https://github.com/user-attachments/assets/3589c016-6188-4dba-aa2f-550de3b61cb4" />


### AI Meal Planner

<img width="938" height="462" alt="image" src="https://github.com/user-attachments/assets/94bac98c-65c8-4a2d-bc2f-d7907eee1856" />


### Shopping List

<img width="932" height="469" alt="image" src="https://github.com/user-attachments/assets/d3e52f9f-0671-49bf-9972-1b49092e2dec" />


---

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- Groq API key

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_PROJECT_FOLDER
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Replace the placeholder with your actual Groq API key.

**Important:** Never upload your actual `.env` file or API key to GitHub.

### 5. Run the Backend

From the project root, execute:

```bash
uvicorn backend.app.main:app --reload
```

The FastAPI documentation will be available at:

http://127.0.0.1:8000/docs

### 6. Run the Frontend

Open a separate terminal, activate the virtual environment, and execute:

```bash
streamlit run frontend/app.py
```

The RecipePilot application will open in your browser.

---

## Project Demonstration

Video demonstration of RecipePilot running locally:

[Watch RecipePilot Demo](https://youtu.be/nH6msVJ7EX8)

---

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key used to access Groq |

---

## Project Information

**Project Name:** RecipePilot

**Project Type:** AI-Powered Recipe Assistant

**Domain:** Artificial Intelligence and Full-Stack Development

**Developed Using:** Python, Streamlit, FastAPI, Groq, ChromaDB and TheMealDB
```
