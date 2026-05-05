import os
from html import escape

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


st.set_page_config(
    page_title="AI Productivity Assistant",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    :root {
        --ink: #17211f;
        --muted: #66736f;
        --line: #d7dfdc;
        --paper: #fbfcfb;
        --panel: #ffffff;
        --mint: #dff3e8;
        --teal: #176b66;
        --coral: #e46f52;
        --gold: #d99b2b;
    }

    .stApp {
        background:
            linear-gradient(135deg, rgba(223, 243, 232, 0.7), rgba(255,255,255,0.25) 34%),
            linear-gradient(180deg, #fbfcfb 0%, #eef5f1 100%);
        color: var(--ink);
    }

    [data-testid="stSidebar"] {
        background: #f5f8f6;
        border-right: 1px solid var(--line);
    }

    .main .block-container {
        padding-top: 1.6rem;
        max-width: 1240px;
    }

    .app-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        border-bottom: 1px solid var(--line);
        padding-bottom: 1rem;
        margin-bottom: 1rem;
    }

    .app-title h1 {
        font-size: clamp(1.6rem, 2.8vw, 2.6rem);
        line-height: 1.05;
        margin: 0;
        letter-spacing: 0;
        color: var(--ink);
    }

    .status-pill {
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 0.45rem 0.75rem;
        background: #ffffff;
        color: var(--teal);
        font-weight: 700;
        white-space: nowrap;
    }

    .metric-row {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.75rem;
        margin: 1rem 0 1.2rem;
    }

    .metric-tile {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem;
        min-height: 104px;
        box-shadow: 0 14px 32px rgba(23, 33, 31, 0.05);
    }

    .metric-tile b {
        color: var(--muted);
        display: block;
        font-size: 0.78rem;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .metric-tile span {
        color: var(--ink);
        display: block;
        font-size: 1.45rem;
        font-weight: 800;
        line-height: 1.15;
    }

    .result-box {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.88);
        padding: 1rem;
        margin-top: 0.75rem;
        box-shadow: 0 14px 32px rgba(23, 33, 31, 0.05);
        white-space: pre-wrap;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.4rem;
        border-bottom: 1px solid var(--line);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px 8px 0 0;
        color: var(--muted);
        height: 44px;
    }

    .stTabs [aria-selected="true"] {
        color: var(--teal);
        background: #ffffff;
        border: 1px solid var(--line);
        border-bottom: 1px solid #ffffff;
    }

    .stButton > button {
        border-radius: 8px;
        border: 1px solid #145f5a;
        background: #176b66;
        color: white;
        font-weight: 800;
        min-height: 42px;
    }

    .stButton > button:hover {
        border-color: #0f4f4b;
        background: #0f5d58;
        color: white;
    }

    .stTextInput input, .stTextArea textarea {
        border-radius: 8px;
    }

    @media (max-width: 900px) {
        .metric-row {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .app-title {
            align-items: flex-start;
            flex-direction: column;
        }
    }

    @media (max-width: 520px) {
        .metric-row {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def post_json(path: str, payload: dict) -> dict:
    response = requests.post(f"{API_URL}{path}", json=payload, timeout=45)
    response.raise_for_status()
    return response.json()


def render_result(text: str) -> None:
    safe_text = escape(text)
    st.markdown(f"<div class='result-box'>{safe_text}</div>", unsafe_allow_html=True)


def show_api_error(error: Exception) -> None:
    if isinstance(error, requests.HTTPError):
        try:
            detail = error.response.json().get("detail", str(error))
        except ValueError:
            detail = error.response.text
        st.error(detail)
        return

    st.error(f"Backend unavailable at {API_URL}. Start FastAPI and try again.")


st.sidebar.title("Workspace")
api_url = st.sidebar.text_input("API URL", value=API_URL)
API_URL = api_url.rstrip("/")
st.sidebar.caption("FastAPI backend")

st.markdown(
    """
    <div class="app-title">
        <h1>AI Productivity Assistant</h1>
        <div class="status-pill">FastAPI + Streamlit</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="metric-row">
        <div class="metric-tile"><b>Tools</b><span>4</span></div>
        <div class="metric-tile"><b>Backend</b><span>FastAPI</span></div>
        <div class="metric-tile"><b>Frontend</b><span>Streamlit</span></div>
        <div class="metric-tile"><b>Focus</b><span>Careers</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

chat_tab, resume_tab, jobs_tab, weather_tab = st.tabs(
    ["Assistant", "Resume Analyzer", "Job Search", "Weather"]
)

with chat_tab:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Ask about jobs, weather, study plans, project ideas, or resume improvements.",
            }
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("Ask the assistant")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking"):
                try:
                    answer = post_json("/chat", {"message": prompt})["response"]
                except Exception as error:
                    show_api_error(error)
                    answer = ""

            if answer:
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

with resume_tab:
    left, right = st.columns([0.95, 1.05], gap="large")

    with left:
        resume_file = st.file_uploader("Resume file", type=["pdf", "txt"])
        job_description = st.text_area("Job description", height=220)
        analyze = st.button("Analyze Resume", use_container_width=True)

    with right:
        if analyze:
            if not resume_file:
                st.warning("Upload a resume first.")
            else:
                with st.spinner("Analyzing resume"):
                    try:
                        response = requests.post(
                            f"{API_URL}/resume/analyze",
                            files={"resume_file": (resume_file.name, resume_file.getvalue(), resume_file.type)},
                            data={"job_description": job_description},
                            timeout=60,
                        )
                        response.raise_for_status()
                        analysis = response.json()
                    except Exception as error:
                        show_api_error(error)
                        analysis = None

                if analysis:
                    score = analysis["score"]
                    st.progress(min(score, 100) / 100)
                    st.metric("Resume score", f"{score}/100")

                    cols = st.columns(3)
                    cols[0].metric("Words", analysis["word_count"])
                    cols[1].metric("Sections", len(analysis["sections_found"]))
                    cols[2].metric("Matches", len(analysis["matched_keywords"]))

                    if analysis["suggestions"]:
                        st.subheader("Suggestions")
                        for item in analysis["suggestions"]:
                            st.write(f"- {item}")

                    if analysis["matched_keywords"]:
                        st.subheader("Matched Keywords")
                        st.write(", ".join(analysis["matched_keywords"]))

                    if analysis["missing_keywords"]:
                        st.subheader("Missing Keywords")
                        st.write(", ".join(analysis["missing_keywords"]))
        else:
            render_result("Upload a resume and add a job description to get a targeted score.")

with jobs_tab:
    job_query = st.text_input("Search query", value="Python developer internship India")
    if st.button("Find Jobs", use_container_width=True):
        with st.spinner("Searching"):
            try:
                result = post_json("/jobs", {"query": job_query})["response"]
                render_result(result)
            except Exception as error:
                show_api_error(error)

with weather_tab:
    location = st.text_input("Location", value="New Delhi")
    if st.button("Get Weather", use_container_width=True):
        with st.spinner("Checking weather"):
            try:
                result = post_json("/weather", {"location": location})["response"]
                render_result(result)
            except Exception as error:
                show_api_error(error)
