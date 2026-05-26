import json
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

_SYSTEM = """You are a legacy code analyser. Analyse the provided code snippet and return ONLY valid JSON with these exact keys:
- "summary": plain-English explanation of what the code does (1-3 sentences)
- "identified_patterns": array of zero or more pattern names from the list below
- "complexity_score": integer 1 (trivial) to 10 (extremely complex)
- "language_detected": detected programming language as a short string

Pattern names and what triggers them:
- GOD_CLASS: a single class/module handling many unrelated responsibilities
- HARDCODED_CONFIG: URLs, IP addresses, server names, or file paths baked into source (NOT credentials — those are caught separately)
- MAGIC_NUMBER: unexplained numeric literals in calculations (e.g. /1200, *0.15, > 50000) with no named constant
- TIGHT_COUPLING: direct instantiation or calls to external modules/classes with no abstraction layer (e.g. Call ExternalModule(), New SomeService)
- NO_ERROR_HANDLING: complete absence of any error handling in code that performs risky operations (file I/O, parsing, external calls) — distinct from silent suppression
- RAW_SQL: SQL queries built by string concatenation without parameterisation
- DEAD_CODE: code that can never be reached or is never called
- NO_INPUT_VALIDATION: user-supplied input (e.g. Request.Form, Request.QueryString, argv, stdin) used directly in logic without any type check, range check, or sanitisation
- SILENT_ERROR_SUPPRESSION: errors are explicitly caught and discarded (e.g. On Error Resume Next with empty handler, catch block with only a comment, bare except: pass)

Rules:
- Use NO_INPUT_VALIDATION when Request.Form / Request.QueryString / user input is used with no validation
- Use SILENT_ERROR_SUPPRESSION (not NO_ERROR_HANDLING) when On Error Resume Next appears with an empty or comment-only error handler
- Use MAGIC_NUMBER when a number like 1200 appears in a formula with no explanation
- Only include patterns that are clearly present — do not guess

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
