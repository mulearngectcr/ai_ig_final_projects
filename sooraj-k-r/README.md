<div align="center">

# 🌴 TripSmith

**An AI-powered, feasibility-first travel planner focused initially on Kerala.**

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-18+-339933?logo=nodedotjs&logoColor=white)
![React](https://img.shields.io/badge/React-Vite-61DAFB?logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-FF5A50)

</div>

---

Unlike standard AI itineraries, TripSmith actively evaluates your budget and constraints using a multi-agent AI workflow and a local RAG (Retrieval-Augmented Generation) database to determine if your trip is actually practical.

## ✨ Features

- 🤖 **Sequential Multi-Agent AI**: Powered by CrewAI (Researcher → Planner → Analyst).
- 🗄️ **Local RAG Database**: Uses ChromaDB and Sentence Transformers for accurate local tourism data.
- 💰 **Feasibility Analysis**: Actively calculates expected costs against user budgets.
- 🎨 **Minimalist UI**: Clean, responsive React frontend with Markdown rendering.

## 📋 Prerequisites

- Python 3.12+
- Node.js 18+
- A free [Groq API Key](https://console.groq.com/keys)

## 🚀 Setup & Installation

### 1. Backend Setup

Navigate to the backend directory and set up your Python environment:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Initialize the local database (only needed once):

```bash
python rag_manager.py
```

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

### 2. Frontend Setup

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend
npm install
```

Start the Vite development server:

```bash
npm run dev
```

## 🧭 Usage

1. Open your browser to **http://localhost:5173**.
2. Enter your starting location, destination (e.g., Munnar), days, travelers, and total budget.
3. Add any specific travel preferences (e.g., *"Tea Gardens, Relaxing"*).
4. Click **"Plan My Trip"**. The AI agents will take ~30-60 seconds to research, plan, and analyze your trip.

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | React, Vite, React-Markdown |
| **Backend** | FastAPI, Pydantic |
| **AI & ML** | CrewAI, ChromaDB, SentenceTransformers, Groq (LLM) |