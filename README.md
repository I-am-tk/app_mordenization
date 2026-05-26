# Legacy Migration Agent API

Accepts legacy code snippets (VB6 / Classic ASP / COBOL / JavaEE), analyses them with GPT-4o via LangChain, assesses migration risk with rule-based logic, generates modernised code, and returns structured migration reports.

## Architecture

```
POST /analyze
  → LangChain + GPT-4o (analysis)
  → Rule-based regex (risk assessment)
  → In-memory storage

POST /migrate/{id}
  → LangChain + GPT-4o (code generation)
  → Rule-based checklist builder
  → In-memory storage (update)

GET /report/{id}   → merge stored analysis + migration
GET /patterns      → static catalogue (no LLM)
```

## Quick Start (Docker — recommended)

```bash
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY

docker-compose up --build
```

API is live at http://localhost:8000  
Swagger UI: http://localhost:8000/docs

## Quick Start (local with uv)

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY

uv sync
uv run uvicorn app.main:app --reload --port 8000
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | OpenAI API key |
| `LLM_MODEL` | No | `gpt-4o` | OpenAI model name |
| `TARGET_FRAMEWORK` | No | `python_fastapi` | Fallback target framework |

Supported frameworks: `python_fastapi`, `dotnet8`, `nodejs_express`, `java_springboot`

## Sample curl Requests

### Analyse a VB6 snippet

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "VB6",
    "code_snippet": "conn.Open \"Provider=SQLOLEDB;Server=192.168.1.10;Database=LoanDB;UID=sa;PWD=Admin123\"\nrs.Open \"SELECT * FROM Loans WHERE Status = '"'"'PENDING'"'"'\", conn",
    "module_name": "LoanProcessor",
    "description": "Legacy loan processing module"
  }'
```

### Generate modernised code

```bash
curl -X POST "http://localhost:8000/migrate/{snippet_id}?target_framework=python_fastapi"
```

### Get full report

```bash
curl http://localhost:8000/report/{snippet_id}
```

### List anti-patterns

```bash
curl http://localhost:8000/patterns
```

## Running Tests

```bash
uv run pytest tests/ -v
```
