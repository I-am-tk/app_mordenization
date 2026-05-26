import json
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

_SYSTEM = """You are a legacy code analyser. Analyse the provided code snippet and return ONLY valid JSON with these exact keys:
- "summary": plain-English explanation of what the code does (1-3 sentences)
- "identified_patterns": array of zero or more strings from exactly: GOD_CLASS, HARDCODED_CONFIG, MAGIC_NUMBER, TIGHT_COUPLING, NO_ERROR_HANDLING, RAW_SQL, DEAD_CODE
- "complexity_score": integer 1 (trivial) to 10 (extremely complex)
- "language_detected": detected programming language as a short string

Return ONLY the raw JSON object. No markdown fences, no explanation, no extra keys."""


def analyse(code: str, language: str) -> dict:
    llm = ChatOpenAI(
        model=os.environ.get("LLM_MODEL", "gpt-4o"),
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=0,
        timeout=30,
    )
    messages = [
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=f"Language hint: {language}\n\nCode:\n{code}"),
    ]
    response = llm.invoke(messages)
    raw = response.content.strip()
    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)
