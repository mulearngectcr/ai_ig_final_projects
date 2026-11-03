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
flowchart TD

    U(["User"])

    subgraph FE["Streamlit Frontend"]
        F1["Recipe Finder and Details"]
        F2["Cooking Assistant - chat history in session state"]
        F3["Recipe Library - PDF upload"]
        F4["AI Meal Planner"]
        F5["Shopping List"]
    end

    subgraph BE["FastAPI Backend"]
        API["API Routes with Pydantic validation"]
        S1["Recipe Search and Details Services"]
        S4["PDF Ingestion Service"]
        S7["Shopping List Service - calls ask_assistant"]
    end

    subgraph AGENT["Agent and Tool Layer"]
        AG["Cooking Assistant Agent - selects a tool or answers directly"]
        T1["search_recipes"]
        T2["search_recipe_library"]
        T3["create_meal_plan"]
        CREW["CrewAI Workflow - verify implementation"]
    end

    subgraph RAPI["Recipe API"]
        MEALDB["TheMealDB API"]
    end

    subgraph LLM["AI / LLM"]
        GROQ["Groq LLM - openai/gpt-oss-20b"]
    end

    subgraph PDFDB["PDF Processing and Vector Database"]
        PYMUPDF["PyMuPDF"]
        CHUNK["Text Chunking - if implemented"]
        ST["Sentence Transformers - chunk embeddings"]
        STQ["Sentence Transformers - question embedding"]
        CHROMA[("ChromaDB")]
    end

    U --> FE
    FE <-->|"HTTP request / JSON response"| API

    %% Recipe Finder and Details
    API <-->|"ingredients / recipe results"| S1
    S1 <-->|"search and lookup / recipes"| MEALDB

    %% Cooking Assistant
    API <-->|"question / answer"| AG
    AG <-->|"prompt / AI response"| GROQ
    AG -->|"selects tool"| T1
    AG -->|"selects tool"| T2
    AG -->|"selects tool"| T3

    T1 <-->|"ingredients / matching recipes"| MEALDB

    %% PDF Question Answering
    T2 -->|"question"| STQ
    STQ -->|"question embedding"| CHROMA
    CHROMA -->|"retrieved chunks"| T2

    %% Meal Planning - connection needs verification
    T3 -.->|"connection to CrewAI - verify"| CREW

    %% PDF Upload and Ingestion
    API <-->|"PDF file / upload status"| S4
    S4 -->|"PDF file"| PYMUPDF
    PYMUPDF -->|"extracted text"| CHUNK
    CHUNK -->|"text chunks"| ST
    ST -->|"embeddings and text"| CHROMA

    %% Shopping List
    API <-->|"list request / shopping list"| S7
    S7 <-->|"prompt / generated list"| GROQ

    %% Styling
    classDef user fill:#eceff1,stroke:#455a64,color:#263238
    classDef frontend fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    classDef backend fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    classDef agent fill:#fffde7,stroke:#f9a825,color:#5d4037
    classDef tool fill:#fff8e1,stroke:#f9a825,color:#5d4037
    classDef recipe fill:#fce4ec,stroke:#c2185b,color:#880e4f
    classDef llm fill:#fff3e0,stroke:#ef6c00,color:#e65100
    classDef pdf fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c

    class U user
    class F1,F2,F3,F4,F5 frontend
    class API,S1,S4,S7 backend
    class AG,CREW agent
    class T1,T2,T3 tool
    class MEALDB recipe
    class GROQ llm
    class PYMUPDF,CHUNK,ST,STQ,CHROMA pdf

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
