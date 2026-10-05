from google import genai
from google.genai import types
from langchain_core.tools import tool

from app.config import GOOGLE_API_KEY

_client = genai.Client(api_key=GOOGLE_API_KEY)


@tool
def google_search(query: str) -> str:
    """
    Search Google for current, real-world information — news, facts, prices,
    events, or anything that may have changed recently or isn't covered by
    other tools. Use this for general web search queries.
    """
    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        contents=query,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        ),
    )
    return response.text