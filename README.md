# AI Productivity Assistant

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-ff4b4b)
![LangChain](https://img.shields.io/badge/AI-LangChain-1f6f43)
![uv](https://img.shields.io/badge/Package%20Manager-uv-5b5bd6)

A full-stack AI productivity assistant for students and job seekers, built with
LangChain, Groq, FastAPI, Streamlit, and custom tools.

The app combines an AI chat assistant with practical career-focused utilities:
resume analysis, job search, live weather, and calculation tools. It is designed
as a portfolio-ready project with a clean API backend and a modern Streamlit UI.

## Highlights

- AI assistant powered by Groq and LangChain
- FastAPI backend with clean REST endpoints
- Streamlit dashboard with a polished multi-tab interface
- Resume analyzer for PDF and TXT resumes
- Job search tool using DuckDuckGo search
- Live weather lookup using weather APIs
- Safe calculator tool without raw `eval`
- `uv` based dependency and environment management

## Tech Stack

| Layer | Tools |
| --- | --- |
| Frontend | Streamlit |
| Backend | FastAPI, Uvicorn |
| AI Agent | LangChain, LangGraph, Groq |
| Tools | Weather API, DuckDuckGo Search, pypdf |
| Environment | uv, python-dotenv |

## Project Structure

```text
.
├── agent.py          # Reusable LangChain agent logic and CLI mode
├── app.py            # Streamlit frontend
├── backend.py        # FastAPI backend
├── tools.py          # Custom tools: weather, jobs, resume analysis, calculator
├── .env.example      # Example environment variables
├── pyproject.toml    # uv project dependencies
├── uv.lock           # Locked dependency versions
└── README.md
```

## Features

### Assistant Chat

Ask general questions, get productivity help, and use the connected tools through
the agent.

Example:

```text
Plan a 7-day schedule to improve my Python and FastAPI skills.
```

### Resume Analyzer

Upload a PDF or TXT resume and optionally paste a job description. The analyzer
returns:

- Resume score
- Word count
- Detected sections
- Matched keywords
- Missing keywords
- Practical improvement suggestions

### Job Search

Search for current jobs by role, skill, or location.

Example:

```text
Python developer internship India
```

### Weather Tool

Get current weather by city or place name.

Example:

```text
New Delhi
```

## Setup

Install dependencies with `uv`:

```bash
uv sync
```

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_weather_api_key
```

You can also use:

```bash
WEATHER_API_KEY=your_weatherapi_key
```

## Run Locally

Start the FastAPI backend:

```bash
uv run uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
```

If port `8000` is already in use, run the backend on port `8001`:

```bash
uv run uvicorn backend:app --host 127.0.0.1 --port 8001 --reload
```

Start the Streamlit frontend in another terminal:

```bash
uv run streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

## Working Local URLs



> **FastAPI Backend:** [`http://127.0.0.1:8001`](http://127.0.0.1:8001)

> **FastAPI Docs:** [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)

> **FastAPI Docs Alternative:** [`http://127.0.0.1:8001/docs`](http://127.0.0.1:8001/docs)

> **Streamlit Frontend:** [`http://127.0.0.1:8501`](http://127.0.0.1:8501)

Open the Streamlit app:

```text
http://127.0.0.1:8501
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Optional CLI Mode

```bash
uv run python agent.py
```

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Health check |
| `POST` | `/chat` | Ask the AI assistant |
| `POST` | `/weather` | Get current weather |
| `POST` | `/jobs` | Search for jobs |
| `POST` | `/resume/analyze` | Analyze a resume file |

## Example API Request

```bash
curl -X POST http://127.0.0.1:8000/weather \
  -H "Content-Type: application/json" \
  -d '{"location": "New Delhi"}'
```

## Deployment Notes

For deployment, set these environment variables in your hosting platform:

```bash
GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_weather_api_key
```

Recommended deployment split:

- Deploy `backend.py` as a FastAPI service.
- Deploy `app.py` as a Streamlit app.
- Set `API_URL` in the Streamlit deployment to your backend URL.

Example:

```bash
API_URL=https://your-fastapi-backend.com
```

## Resume Project Summary

Built a full AI productivity assistant using LangChain, Groq, FastAPI, and
Streamlit, featuring custom tools for resume analysis, job search, weather
lookup, and safe calculations with a clean  and interactive dashboard.

## License

This project is open for learning, portfolio use, and further customization.
