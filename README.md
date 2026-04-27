# ⚡ AlgoLens — AI-Powered DSA Problem Analyzer

AlgoLens analyzes any DSA problem statement and instantly returns the optimal algorithm pattern, time/space complexity, and an AI-generated step-by-step explanation powered by LLaMA 3 via Groq.

## 🚀 Features
- Classifies problems into 10 DSA patterns (DP, Graphs, Sliding Window, etc.)
- Returns time and space complexity estimates
- Generates approach, pseudocode, and key insight using LLM
- REST API built with FastAPI
- Clean dark-themed frontend UI

## 🛠 Tech Stack
- Python, FastAPI, Groq API (LLaMA 3.3)
- HTML/CSS/JavaScript

## ⚙️ Setup
```bash
git clone https://github.com/errorinloading/AlgoLens.git
cd AlgoLens
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your GROQ_API_KEY
cd backend
uvicorn main:app --reload
```
Then open `frontend/index.html` in your browser.

## 📡 API Endpoints
- `GET /` — Health check
- `POST /analyze` — Analyze a DSA problem
- `GET /patterns` — List all supported patterns

## 🧠 Supported Patterns
Dynamic Programming, Sliding Window, Two Pointers, Binary Search, Graph/BFS/DFS, Stack/Queue, Backtracking, Greedy, Hashing, Linked List
