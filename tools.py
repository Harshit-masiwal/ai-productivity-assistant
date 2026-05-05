import ast
import os
import operator
import re
from collections import Counter

from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchResults
from langchain.tools import tool
import requests

load_dotenv()


ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


@tool
def calculator(expression: str) -> str:
    """Safely calculate a basic math expression."""
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_evaluate_math_node(tree.body))
    except Exception:
        return "Invalid expression"


def _evaluate_math_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](
            _evaluate_math_node(node.left),
            _evaluate_math_node(node.right),
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](_evaluate_math_node(node.operand))
    raise ValueError("Unsupported expression")


WEATHER_API_KEY = os.getenv("WEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")


@tool
def get_weather(location: str) -> str:
    """Get the current weather for a city or place name."""
    if not WEATHER_API_KEY:
        return "Weather API key is missing. Add WEATHER_API_KEY or OPENWEATHER_API_KEY to your .env file."

    weatherapi_result = _get_weather_from_weatherapi(location)
    if weatherapi_result:
        return weatherapi_result

    openweather_result = _get_weather_from_openweather(location)
    if openweather_result:
        return openweather_result

    return f"Could not fetch weather for {location}. Please check the city name or API key."


def _get_weather_from_weatherapi(location: str) -> str | None:
    url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": location,
        "aqi": "no",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None

    current = data.get("current", {})
    place = data.get("location", {})
    condition = current.get("condition", {}).get("text", "Unknown")

    temp_c = current.get("temp_c")
    feels_like_c = current.get("feelslike_c")
    humidity = current.get("humidity")
    wind_kph = current.get("wind_kph")
    place_name = ", ".join(
        part for part in [place.get("name"), place.get("region"), place.get("country")] if part
    )

    return (
        f"Current weather in {place_name or location}: {temp_c}°C, {condition}. "
        f"Feels like {feels_like_c}°C. Humidity {humidity}%. Wind {wind_kph} kph."
    )


def _get_weather_from_openweather(location: str) -> str | None:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "appid": WEATHER_API_KEY,
        "q": location,
        "units": "metric",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None

    weather = data.get("weather", [{}])[0]
    main = data.get("main", {})
    wind = data.get("wind", {})

    place_name = data.get("name") or location
    country = data.get("sys", {}).get("country")
    condition = weather.get("description", "unknown conditions").title()
    temp_c = main.get("temp")
    feels_like_c = main.get("feels_like")
    humidity = main.get("humidity")
    wind_kph = round((wind.get("speed") or 0) * 3.6, 1)

    if country:
        place_name = f"{place_name}, {country}"

    return (
        f"Current weather in {place_name}: {temp_c}°C, {condition}. "
        f"Feels like {feels_like_c}°C. Humidity {humidity}%. Wind {wind_kph} kph."
    )


@tool
def search_jobs(query: str) -> str:
    """Search the web for current job openings by role, skill, or location."""
    search = DuckDuckGoSearchResults(output_format="list")
    results = search.invoke(f"{query} jobs hiring careers apply")

    if not results:
        return "No job results found. Try a more specific role and location."

    lines = []
    for index, item in enumerate(results[:6], start=1):
        title = item.get("title", "Untitled result")
        link = item.get("link") or item.get("href") or ""
        snippet = item.get("snippet", "").strip()
        lines.append(f"{index}. {title}\n{snippet}\n{link}".strip())

    return "\n\n".join(lines)


def analyze_resume_text(resume_text: str, job_description: str = "") -> dict:
    resume_text = _clean_text(resume_text)
    job_description = _clean_text(job_description)

    resume_words = _keyword_counts(resume_text)
    job_words = _keyword_counts(job_description)

    if job_words:
        required_keywords = set(job_words)
        matched_keywords = sorted(required_keywords & set(resume_words))
        missing_keywords = sorted(required_keywords - set(resume_words))
        match_score = round((len(matched_keywords) / max(len(required_keywords), 1)) * 100)
    else:
        matched_keywords = []
        missing_keywords = []
        match_score = _general_resume_score(resume_text)

    sections_found = [
        section for section in ["experience", "projects", "skills", "education", "certifications"]
        if section in resume_text.lower()
    ]

    suggestions = _resume_suggestions(resume_text, missing_keywords, sections_found)

    return {
        "score": match_score,
        "word_count": len(resume_text.split()),
        "sections_found": sections_found,
        "matched_keywords": matched_keywords[:20],
        "missing_keywords": missing_keywords[:20],
        "top_resume_keywords": [word for word, _ in resume_words.most_common(15)],
        "suggestions": suggestions,
    }


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _keyword_counts(text: str) -> Counter:
    stop_words = {
        "and", "the", "with", "for", "from", "that", "this", "your", "you", "are",
        "will", "have", "has", "our", "their", "they", "into", "using", "use",
        "role", "work", "team", "job", "about", "based", "skills", "experience",
    }
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}", text.lower())
    return Counter(word for word in words if word not in stop_words)


def _general_resume_score(text: str) -> int:
    score = 45
    lower_text = text.lower()
    for section in ["experience", "projects", "skills", "education"]:
        if section in lower_text:
            score += 8
    if re.search(r"\b\d+%|\b\d+x|\b\d+\+", text):
        score += 10
    if len(text.split()) >= 350:
        score += 8
    return min(score, 95)


def _resume_suggestions(text: str, missing_keywords: list[str], sections_found: list[str]) -> list[str]:
    suggestions = []
    lower_text = text.lower()

    if "projects" not in sections_found:
        suggestions.append("Add a Projects section with 2-3 practical projects and measurable outcomes.")
    if "skills" not in sections_found:
        suggestions.append("Add a clear Skills section grouped by languages, frameworks, tools, and databases.")
    if not re.search(r"\b\d+%|\b\d+x|\b\d+\+", text):
        suggestions.append("Add numbers to achievements, such as accuracy, users, latency, cost, or time saved.")
    if missing_keywords:
        suggestions.append(f"Add relevant job-description keywords: {', '.join(missing_keywords[:8])}.")
    if len(text.split()) < 250:
        suggestions.append("Add more detail to experience and projects so recruiters can understand your impact.")
    if "langchain" not in lower_text and "agent" not in lower_text:
        suggestions.append("Mention your AI agent project with LangChain, FastAPI, Streamlit, APIs, and custom tools.")

    return suggestions[:6]
