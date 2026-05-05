from dotenv import load_dotenv
import os

load_dotenv()

from groq import APIConnectionError, AuthenticationError
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_community.tools import DuckDuckGoSearchResults

from tools import get_weather, calculator, search_jobs

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY is missing. Add it to your .env file.")

search = DuckDuckGoSearchResults()

model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
    api_key=groq_api_key
)

agent = create_agent(
    model=model,
    tools=[search, get_weather, calculator, search_jobs],
    system_prompt=(
        "You are a practical AI productivity assistant for students and job seekers. "
        "Use tools when they help. When a tool returns a direct answer, summarize it "
        "plainly and do not mention implementation details."
    ),
)


def extract_weather_location(user_input: str) -> str | None:
    text = user_input.strip()
    lower_text = text.lower()

    if "weather" not in lower_text:
        return None

    for phrase in ["weather in ", "weather for ", "weather at ", "weather of "]:
        if phrase in lower_text:
            start = lower_text.index(phrase) + len(phrase)
            return text[start:].strip(" ?.!")

    if lower_text.startswith("weather "):
        return text[len("weather "):].strip(" ?.!") or None

    return None


def ask_agent(user_input: str) -> str:
    weather_location = extract_weather_location(user_input)
    if weather_location:
        return get_weather.invoke({"location": weather_location})

    try:
        response = agent.invoke({
            "messages": [("user", user_input)]
        })
    except AuthenticationError:
        return "Your GROQ_API_KEY was rejected. Please check the key in your .env file."
    except APIConnectionError:
        return "I could not connect to Groq. Please check your internet connection and try again."
    except Exception as error:
        return f"Something went wrong: {error}"

    return response["messages"][-1].content


def main() -> None:
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() == "exit":
            break
        if not user_input:
            continue

        print("\nAI:", ask_agent(user_input))


if __name__ == "__main__":
    main()
