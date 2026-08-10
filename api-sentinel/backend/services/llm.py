"""
services/llm.py
----------------
The ONLY job of this file: take raw pasted API documentation text and
extract { name, url, method } using an LLM (via Groq, through LangChain).

Important (per the spec):
- The LLM is only used for extraction, never for monitoring.
- If this fails for any reason, manual API addition must still work
  (this file never gets called during monitoring, only during import).
"""

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

_llm = (
    ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
        temperature=0,
    )
    if GROQ_API_KEY
    else None
)

EXTRACTION_SYSTEM_PROMPT = """You are an API documentation extraction assistant.
You will be given raw API documentation text.
Extract ONLY the following fields and respond with STRICT JSON and nothing else,
no preamble, no markdown fences:

{
  "name": "short human readable API name",
  "url": "the full endpoint URL",
  "method": "GET | POST | PUT | DELETE"
}"""


def extract_api_info(documentation_text: str) -> dict:
    """
    Returns a dict: {"name": ..., "url": ..., "method": ...}
    Raises an exception if extraction fails -- the router is responsible
    for turning that into a clean HTTP error so the frontend can fall
    back to manual entry.
    """
    if _llm is None:
        raise RuntimeError("GROQ_API_KEY is not configured on the backend")

    response = _llm.invoke(
        [
            SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(content=f"Documentation:\n---\n{documentation_text}\n---"),
        ]
    )

    raw_text = response.content.strip()

    # Defensive cleanup in case the model wraps the JSON in code fences
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    data = json.loads(raw_text)

    if not all(k in data for k in ("name", "url", "method")):
        raise ValueError("LLM response missing required fields")

    data["method"] = str(data["method"]).upper()
    if data["method"] not in {"GET", "POST", "PUT", "DELETE"}:
        data["method"] = "GET"

    return data