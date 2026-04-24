# 🕵️‍♂️ Automated Candidate Scanner (Multi-Agent)

An intelligent, multi-agent recruitment CRM that takes natural language queries, automatically routes searches to the best platforms (LinkedIn, GitHub, Kaggle, etc.), evaluates profiles using a strict quality rubric, and returns the "cream of the crop".

Powered by **Streamlit**, **DuckDuckGo Search**, and **Google Gemini 2.5 Flash**.

---

## 🏗️ Multi-Agent Architecture
This tool uses a 3-Agent pipeline to find top-tier candidates without hallucinating credentials:
1. **Agent 1 (Strategy)**: Analyzes your query and decides the best platforms (e.g., routing "Data Engineer" to Kaggle + GitHub, and "UI/UX" to Behance).
2. **Agent 2 (Retrieval)**: Generates broad search queries and scrapes raw candidate profiles directly from the chosen platforms.
3. **Agent 3 (Evaluation)**: Acts as a strict technical recruiter. It reads the raw data, evaluates the candidate on a dynamic 0-100 rubric, extracts elite traits, filters out buzzword fluff, and sorts the final list by quality.

---

## 🚀 Quick Setup Guide

Yes, it is incredibly simple to set up! Just clone the repository and run three steps:

### 1. Install Dependencies
We use `uv` for blazing-fast package management. Run the following to install everything instantly:
```bash
uv sync
```

### 2. Configure API Key
1. Copy the `.env.example` file and rename it to `.env`.
2. Get your free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
3. Paste it into the `.env` file:
```env
GEMINI_API_KEY="your_api_key_here"
```

### 3. Start the App
Start the Streamlit UI (which will automatically pop open in your browser at `http://localhost:8501`):
```bash
uv run streamlit run app.py
```

---

## 🎨 Features
- **Dark Mode Aesthetic**: A premium, glassmorphic UI.
- **Dynamic Scoring**: Automatically shifts expectations. (e.g., Rewards "leading teams" for Seniors, but rewards "IIT/NIT" and "Competitive Programming" for Freshers).
- **One-Click CSV Export**: Download your curated list of elite candidates instantly.
