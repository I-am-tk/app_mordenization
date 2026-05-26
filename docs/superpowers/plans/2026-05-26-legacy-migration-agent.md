# Legacy Migration Agent — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a FastAPI REST API that analyses legacy code (VB6/ASP/COBOL/JavaEE), assesses risk, generates modernised code via LangChain + GPT-4o, and returns structured migration reports.

**Architecture:** Six focused app modules (models, storage, patterns, risk_engine, analyser, code_generator, checklist_builder, report_assembler) wired together by main.py. In-memory dict storage. Rule-based risk engine (no LLM). LangChain for LLM calls.

**Tech Stack:** Python 3.12, FastAPI, LangChain + langchain-openai, Pydantic v2, uv, Docker + docker-compose, Swagger UI (FastAPI built-in at /docs)

---

## Files

| File | Responsibility |
|---|---|
| `pyproject.toml` | uv project + deps |
| `Dockerfile` | Python 3.12-slim, uv sync, uvicorn entrypoint |
| `docker-compose.yml` | Single service, env_file .env, port 8000 |
| `.env.example` | OPENAI_API_KEY, LLM_MODEL, TARGET_FRAMEWORK |
| `app/models.py` | All Pydantic v2 request/response models + enums |
| `app/storage.py` | Thread-safe in-memory dict |
| `app/patterns.py` | Static anti-patterns catalogue |
| `app/risk_engine.py` | Pure regex risk assessment |
| `app/analyser.py` | LangChain → summary, patterns[], complexity |
| `app/code_generator.py` | LangChain → modernised code |
| `app/checklist_builder.py` | Rule-based actionable tasks |
| `app/report_assembler.py` | Merge analysis + migration into report |
| `app/main.py` | FastAPI routes + logging middleware |
| `tests/test_risk_engine.py` | Unit tests for risk_engine |
| `tests/test_api.py` | Integration tests via TestClient |
| `README.md` | Setup, env vars, curl examples, architecture |

---

## Parallel Implementation Waves

### Wave 1 (all parallel)

- **Agent 1** → Infrastructure: uv init, pyproject.toml, Dockerfile, docker-compose.yml, .env.example, .gitignore
- **Agent 2** → Data layer: app/models.py, app/storage.py, app/patterns.py
- **Agent 3** → Business logic: app/risk_engine.py, app/checklist_builder.py, app/report_assembler.py
- **Agent 4** → LLM + API + Tests + README: app/analyser.py, app/code_generator.py, app/main.py, tests/, README.md

### Wave 2

- Verify all files exist, run `uv sync`, `docker-compose build`, confirm Swagger at /docs
