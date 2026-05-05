from io import BytesIO
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import ask_agent
from tools import analyze_resume_text, get_weather, search_jobs

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


app = FastAPI(
    title="AI Productivity Assistant API",
    description="FastAPI backend for chat, weather, job search, and resume analysis.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ToolRequest(BaseModel):
    query: str


class WeatherRequest(BaseModel):
    location: str


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok", "app": "AI Productivity Assistant API"}


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    return {"response": ask_agent(request.message)}


@app.post("/weather")
def weather(request: WeatherRequest) -> dict[str, str]:
    if not request.location.strip():
        raise HTTPException(status_code=400, detail="Location cannot be empty.")

    return {"response": get_weather.invoke({"location": request.location})}


@app.post("/jobs")
def jobs(request: ToolRequest) -> dict[str, str]:
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Job search query cannot be empty.")

    return {"response": search_jobs.invoke({"query": request.query})}


@app.post("/resume/analyze")
async def analyze_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(""),
) -> dict[str, Any]:
    resume_text = await _extract_upload_text(resume_file)

    if len(resume_text.split()) < 30:
        raise HTTPException(
            status_code=400,
            detail="Could not extract enough resume text. Upload a text-based PDF or TXT file.",
        )

    analysis = analyze_resume_text(resume_text, job_description)
    analysis["filename"] = resume_file.filename

    return analysis


async def _extract_upload_text(upload: UploadFile) -> str:
    content = await upload.read()
    filename = (upload.filename or "").lower()

    if filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")

    if filename.endswith(".pdf"):
        if PdfReader is None:
            raise HTTPException(
                status_code=500,
                detail="PDF support needs pypdf. Run: pip install pypdf",
            )
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    raise HTTPException(status_code=400, detail="Please upload a PDF or TXT resume.")
