import os
from app.config import OPENAI_API_KEY, GROQ_API_KEY, GOOGLE_API_KEY

from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


open_ai = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
groq = ChatGroq(model="qwen/qwen3-32b",api_key=GROQ_API_KEY)
ollama = ChatOllama(model='gpt-oss:120b-cloud')
gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=GOOGLE_API_KEY)

fallback_llm = ollama.with_fallbacks([open_ai,groq,gemini])