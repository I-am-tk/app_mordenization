# Legacy Application Modernization & Migration Agent

A REST API and browser-based UI that accepts legacy code snippets — VB6, Classic ASP, COBOL, and JavaEE — and produces structured migration reports. It analyses each snippet using GPT-4o via LangChain to identify anti-patterns and architectural concerns, assesses migration risk through rule-based regex logic (no LLM involved in risk scoring), generates modernised equivalent code in a target framework of your choice, and builds an actionable migration checklist. The result is a complete, machine-readable report that gives engineering teams a clear starting point for modernisation work. A built-in browser UI makes it easy to explore the tool without writing any API calls.

## Features

- Accepts snippets in VB6, Classic ASP, COBOL, and JavaEE
- Detects anti-patterns including hardcoded credentials, raw SQL, missing error handling, and legacy coupling
- Assigns risk levels (CRITICAL / HIGH / MEDIUM / LOW) using deterministic regex rules — no LLM for risk
- Generates modernised code in a configurable target framework via GPT-4o
- Produces a migration checklist alongside the generated code
- Returns a combined structured report per snippet
- Swagger UI available at `/docs` for interactive exploration

## Prerequisites

**Docker (recommended)**
- Docker
- docker-compose

**Local**
- Python 3.12
- [uv](https://github.com/astral-sh/uv)

## Setup

### Docker (recommended)

```bash
cp .env.example .env
# Open .env and set OPENAI_API_KEY
docker compose up --build
```

The API will be available at `http://localhost:8000`.

### Local with uv

```bash
cp .env.example .env
# Open .env and set OPENAI_API_KEY
uv sync
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Browser UI

A built-in web interface is available — no extra setup needed.

Open **http://localhost:8000/ui** after starting the server.

**How to use:**
1. Select the legacy language (VB6, Classic ASP, JavaEE, COBOL) and enter a module name
2. Paste the legacy code snippet and click **Analyze Code**
3. Review the risk level, detected anti-patterns, complexity score, and GPT-4o summary
4. Click **Generate Migration** to get modernised code with inline comments and an actionable checklist

The Swagger UI (interactive API docs) is also available at http://localhost:8000/docs.

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | OpenAI API key used by LangChain |
| `LLM_MODEL` | No | `gpt-4o` | OpenAI model name passed to LangChain |
| `TARGET_FRAMEWORK` | No | `python_fastapi` | Default target framework when none is specified in the request |

## API Reference

Swagger UI with full request/response schemas is available at `http://localhost:8000/docs`.

| Method | Path | Description |
|---|---|---|
| `POST` | `/analyze?target_framework=<fw>` | Analyse a legacy snippet; returns detected patterns and risk level |
| `POST` | `/migrate/{snippet_id}` | Generate modernised code and migration checklist for an analysed snippet |
| `GET` | `/report/{snippet_id}` | Retrieve the full combined report (analysis + migration) for a snippet |
| `GET` | `/patterns` | List all detectable anti-patterns and their descriptions |

## Example Walkthrough

The following three steps take a VB6 loan-processing snippet from raw legacy code to a full migration report.

### Step 1 — Analyse the snippet

```bash
curl -X POST "http://localhost:8000/analyze?target_framework=python_fastapi" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "VB6",
    "code_snippet": "Dim conn As New ADODB.Connection\nconn.Open \"Provider=SQLOLEDB;Server=192.168.1.10;Database=LoanDB;UID=sa;PWD=Admin123\"\nDim rs As New ADODB.Recordset\nrs.Open \"SELECT * FROM Loans WHERE Status = '\''PENDING'\''\", conn\nDo While Not rs.EOF\n  If rs(\"Amount\") > 50000 Then\n    rs(\"Status\") = \"HIGH_RISK\"\n    rs.Update\n  End If\n  rs.MoveNext\nLoop",
    "module_name": "LoanProcessor",
    "description": "Legacy VB6 loan processing module"
  }'
```

The response includes a `snippet_id`, detected patterns (hardcoded credentials, raw SQL), and a risk level. Because this snippet contains hardcoded credentials, the risk level will be `CRITICAL` and migration status `BLOCKED`.

### Step 2 — Generate modernised code

Replace `<snippet_id>` with the value returned in Step 1.

```bash
curl -X POST "http://localhost:8000/migrate/<snippet_id>"
```

The response contains the modernised FastAPI equivalent of the snippet and a migration checklist of steps required before the code is production-ready.

### Step 3 — Retrieve the full report

```bash
curl "http://localhost:8000/report/<snippet_id>"
```

The response merges the analysis from Step 1 and the migration output from Step 2 into a single structured report.

## Risk Levels

Risk is assessed by deterministic regex rules. No LLM is involved in this step.

| Risk Level | Trigger |
|---|---|
| `CRITICAL` | Hardcoded credentials or connection strings |
| `HIGH` | Raw SQL without ORM or parameterisation |
| `MEDIUM` | Missing error handling (`On Error Resume Next`, empty catch blocks) |
| `LOW` | Simple logic with no external dependencies |

Migration status is derived from risk level:

| Risk Level | Migration Status |
|---|---|
| `CRITICAL` | `BLOCKED` |
| `HIGH` / `MEDIUM` | `NEEDS_REVIEW` |
| `LOW` | `READY` |

## Running Tests

No API key is required. The LLM is mocked in the test suite.

```bash
uv run --with pytest pytest tests/ -v
```

## Quick Test Example

Paste this VB6 snippet into the UI to see a full CRITICAL-risk analysis and migration:

**Settings:** Language = VB6 · Module Name = `LoanProcessor` · Framework = Python FastAPI

**Code:**
```vb
'VB6 - Legacy Loan Processing Module
Dim conn As New ADODB.Connection
conn.Open "Provider=SQLOLEDB;Server=192.168.1.10;Database=LoanDB;UID=sa;PWD=Admin123"
Dim rs As New ADODB.Recordset
rs.Open "SELECT * FROM Loans WHERE Status = 'PENDING'", conn
Do While Not rs.EOF
  If rs("Amount") > 50000 Then
    rs("Status") = "HIGH_RISK"
    rs.Update
  End If
  rs.MoveNext
Loop
```

**Expected results:**
- Risk level: **CRITICAL** (hardcoded credentials + raw SQL detected)
- Patterns: `HARDCODED_CONFIG`, `RAW_SQL`, `NO_ERROR_HANDLING`
- Migration status: **BLOCKED**
- Modernised output: FastAPI + SQLAlchemy with environment-variable config and parameterised queries

## Project Structure

```
app/
├── main.py          # FastAPI application entry point and route definitions
├── models.py        # Pydantic v2 request and response schemas
├── analyzer.py      # LangChain + GPT-4o analysis chain
├── risk.py          # Rule-based regex risk assessment (no LLM)
├── migrator.py      # LangChain + GPT-4o code generation and checklist builder
├── storage.py       # In-memory snippet store
└── patterns.py      # Static catalogue of detectable anti-patterns
```

## Supported Target Frameworks

| Value | Description |
|---|---|
| `python_fastapi` | Python 3.12 with FastAPI and SQLAlchemy |
| `dotnet8` | C# with ASP.NET Core 8 and Entity Framework |
| `nodejs_express` | Node.js with Express and Prisma |
| `java_springboot` | Java 21 with Spring Boot 3 and JPA |
