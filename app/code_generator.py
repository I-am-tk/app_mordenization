import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

_SYSTEM = """You are a code modernisation expert. Convert the provided legacy code to idiomatic {framework} code.

Requirements:
- Add inline comments (# or // as appropriate) on EVERY significant change explaining WHY it changed
- Use modern patterns: async/await, dependency injection, ORM, proper error handling, env-based config
- Return ONLY the modernised source code as plain text — no markdown fences, no explanation outside comments"""


def generate(code: str, original_language: str, target_framework: str) -> str:
    llm = ChatOpenAI(
        model=os.environ.get("LLM_MODEL", "gpt-4o"),
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=0,
        timeout=30,
    )
    system = _SYSTEM.format(framework=target_framework)
    messages = [
        SystemMessage(content=system),
        HumanMessage(
            content=f"Original language: {original_language}\nTarget framework: {target_framework}\n\nCode to modernise:\n{code}"
        ),
    ]
    response = llm.invoke(messages)
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return raw
