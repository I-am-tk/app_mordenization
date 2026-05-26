# Legacy Application Modernization & Migration Agent — Design Spec

**Date:** 2026-05-26  
**Status:** Approved

---

## Overview

A REST API that accepts legacy code snippets (VB6, Classic ASP, COBOL, JavaEE), analyses them with an LLM, assesses migration risk via rule-based logic, generates modernised equivalent code, builds an actionable checklist, and returns a full structured migration report.

---

## Pipeline

```
Legacy Code Input
  → LLM Code Analyser        (OpenAI gpt-4o)
  → Rule-Based Risk Assessor (regex only, no LLM)
  → LLM Modern Code Generator (OpenAI gpt-4o)
  → Checklist Builder        (rule-based)
  → Migration Report via API
```

---

## Project Layout

```
legacy-migration-agent/
├── app/
│   ├── main.py              # FastAPI app + all route handlers
│   ├── models.py            # Pydantic v2 request/response models
│   ├── storage.py           # In-memory dict keyed by snippet_id
│   ├── analyser.py          # LLM → summary, patterns[], complexity_score
│   ├── risk_engine.py       # Pure regex → risk_level, risk_reasons[]
│   ├── code_generator.py    # LLM → modernized_code with inline comments
│   ├── checklist_builder.py # Derives actionable tasks from risk + patterns
│   └── report_assembler.py  # Merges analysis + migration into full report
├── .env.example
├── pyproject.toml           # managed by uv
└── README.md
```

---

## Endpoints

### POST /analyze?target_framework=\<framework\>

**Input:**
```json
{
  "language": "VB6 | ClassicASP | JavaEE | COBOL",
  "code_snippet": "<string>",
  "module_name": "<string>",
  "description": "<optional string>"
}
```

**Steps:**
1. Validate input (Pydantic) — HTTP 422 on failure
2. Assign UUID `snippet_id`, log timestamp + module_name
3. Call `analyser.py` (LLM): returns summary, identified_patterns[], complexity_score, language_detected
4. Call `risk_engine.py` (pure regex): returns risk_level, risk_reasons[]
5. Store merged result in `storage.py`

**Output:**
```json
{
  "snippet_id": "<uuid>",
  "summary": "<string>",
  "identified_patterns": [],
  "complexity_score": 0,
  "language_detected": "<string>",
  "risk_level": "CRITICAL|HIGH|MEDIUM|LOW",
  "risk_reasons": []
}
```

---

### POST /migrate/{snippet_id}?target_framework=\<framework\>

**Steps:**
1. Look up snippet by `snippet_id` — HTTP 404 if missing
2. Resolve framework: query param → `TARGET_FRAMEWORK` env var → `python_fastapi`
3. Call `code_generator.py` (LLM): modernized code with inline change comments
4. Call `checklist_builder.py` (rule-based): actionable tasks from risk + patterns
5. Derive `migration_status` from risk_level (see table below)
6. Update storage with migration result

**Output:**
```json
{
  "snippet_id": "<uuid>",
  "modernized_code": "<string>",
  "target_framework": "<string>",
  "migration_checklist": [],
  "migration_status": "READY|NEEDS_REVIEW|BLOCKED"
}
```

---

### GET /report/{snippet_id}

Returns full merged report combining analysis + migration data.

---

### GET /patterns

Returns static list of all detectable anti-patterns (name + description). No LLM.

---

## Risk Assessment Rules (regex, no LLM)

| Rule | Trigger | Risk Level |
|---|---|---|
| Hardcoded credentials / connection strings | `PWD=`, `Password=`, `UID=`, IP literals in conn strings | CRITICAL |
| Raw SQL without ORM/parameterisation | `SELECT *`, `INSERT INTO`, `UPDATE … SET`, `DELETE FROM` as bare strings | HIGH |
| No error handling | `On Error Resume Next`, empty catch `{}`, bare `except: pass` | MEDIUM |
| Simple logic, no external deps | None of the above patterns found | LOW |

**Multiple rules can match** — highest severity wins for `risk_level`; all matching reasons accumulated in `risk_reasons[]`.

---

## Migration Status Rules

| risk_level | migration_status |
|---|---|
| CRITICAL | BLOCKED |
| HIGH | NEEDS_REVIEW |
| MEDIUM | NEEDS_REVIEW |
| LOW | READY |

---

## Anti-Patterns Catalogue

| ID | Name | Description |
|---|---|---|
| GOD_CLASS | God Class | Single class/module doing too many unrelated things |
| HARDCODED_CONFIG | Hardcoded Config | Config values (URLs, IPs, credentials) baked into source |
| MAGIC_NUMBER | Magic Number | Unexplained numeric literals in logic |
| TIGHT_COUPLING | Tight Coupling | Components directly instantiating or calling each other |
| NO_ERROR_HANDLING | No Error Handling | Missing try/catch or silent error suppression |
| RAW_SQL | Raw SQL | Unparameterised SQL queries concatenated as strings |
| DEAD_CODE | Dead Code | Unreachable or never-called code blocks |

---

## Supported Target Frameworks

- `python_fastapi`
- `dotnet8`
- `nodejs_express`
- `java_springboot`

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI API key | required |
| `LLM_MODEL` | Model name | `gpt-4o` |
| `TARGET_FRAMEWORK` | Fallback framework | `python_fastapi` |

---

## Non-Functional Requirements

- LLM calls complete < 5 seconds for snippets ≤ 100 lines
- HTTP 422 for missing/malformed input — never crash
- Every request logged with snippet_id, timestamp, module_name
- All secrets loaded from env vars — never hardcoded
- Project managed with `uv`

---

## Acceptance Criteria

| AC | Criterion |
|---|---|
| AC-1 | POST /analyze returns HTTP 200 with snippet_id, summary, identified_patterns[], complexity_score |
| AC-2 | Snippet with hardcoded DB string → risk_level = CRITICAL, risk_reasons contains HARDCODED_CREDENTIALS |
| AC-3 | POST /migrate/{snippet_id} returns modernized_code with inline change comments |
| AC-4 | Snippet with "On Error Resume Next" → migration_checklist includes error handling task |
| AC-5 | GET /patterns returns HTTP 200 with all anti-patterns listed |
| AC-6 | POST /analyze with missing code_snippet → HTTP 422 with structured validation error |
