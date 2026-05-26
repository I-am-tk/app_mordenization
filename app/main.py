import logging
import os
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

from app import (  # noqa: E402  (after load_dotenv)
    analyser,
    checklist_builder,
    code_generator,
    report_assembler,
    risk_engine,
    storage,
)
from app.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    MigrateResponse,
    MigrationStatus,
    RiskLevel,
)
from app.patterns import ANTI_PATTERNS

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Legacy Migration Agent",
    description=(
        "Accepts legacy code snippets (VB6 / Classic ASP / COBOL / JavaEE), "
        "analyses them with GPT-4o, assesses migration risk, generates modernised "
        "code, and returns structured migration reports.\n\n"
        "**Swagger UI is right here — expand any endpoint and click Try it out.**"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/ui", include_in_schema=False)
async def serve_ui():
    from fastapi.responses import FileResponse
    return FileResponse("app/static/index.html")

_RISK_TO_STATUS: dict[str, MigrationStatus] = {
    "CRITICAL": MigrationStatus.BLOCKED,
    "HIGH": MigrationStatus.NEEDS_REVIEW,
    "MEDIUM": MigrationStatus.NEEDS_REVIEW,
    "LOW": MigrationStatus.READY,
}


def _resolve_framework(query_param: str | None) -> str:
    return query_param or os.getenv("TARGET_FRAMEWORK", "python_fastapi")


@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyse a legacy code snippet",
    tags=["Analysis"],
)
async def analyze_snippet(
    body: AnalyzeRequest,
    target_framework: str | None = Query(default=None, description="Override target framework"),
):
    snippet_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    logger.info(
        "snippet_id=%s module=%s language=%s action=analyse",
        snippet_id,
        body.module_name,
        body.language.value,
    )

    llm_result = analyser.analyse(body.code_snippet, body.language.value)
    risk_level, risk_reasons = risk_engine.assess(body.code_snippet)

    record: dict = {
        "snippet_id": snippet_id,
        "timestamp": timestamp,
        "language": body.language.value,
        "code_snippet": body.code_snippet,
        "module_name": body.module_name,
        "description": body.description,
        "summary": llm_result["summary"],
        "identified_patterns": llm_result["identified_patterns"],
        "complexity_score": llm_result["complexity_score"],
        "language_detected": llm_result["language_detected"],
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
    }
    storage.save(snippet_id, record)

    return AnalyzeResponse(
        snippet_id=snippet_id,
        summary=llm_result["summary"],
        identified_patterns=llm_result["identified_patterns"],
        complexity_score=llm_result["complexity_score"],
        language_detected=llm_result["language_detected"],
        risk_level=RiskLevel(risk_level),
        risk_reasons=risk_reasons,
    )


@app.post(
    "/migrate/{snippet_id}",
    response_model=MigrateResponse,
    summary="Generate modernised code for an analysed snippet",
    tags=["Migration"],
)
async def migrate_snippet(
    snippet_id: str,
    target_framework: str | None = Query(default=None, description="Override target framework"),
):
    record = storage.get(snippet_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"snippet_id '{snippet_id}' not found — run POST /analyze first")

    framework = _resolve_framework(target_framework)

    logger.info(
        "snippet_id=%s module=%s framework=%s action=migrate",
        snippet_id,
        record.get("module_name", ""),
        framework,
    )

    modernized = code_generator.generate(record["code_snippet"], record["language"], framework)
    checklist = checklist_builder.build(
        record["module_name"], record["risk_reasons"], record["identified_patterns"]
    )
    status = _RISK_TO_STATUS[record["risk_level"]]

    storage.update(snippet_id, {
        "modernized_code": modernized,
        "migration_checklist": checklist,
        "target_framework": framework,
        "migration_status": status.value,
    })

    return MigrateResponse(
        snippet_id=snippet_id,
        modernized_code=modernized,
        target_framework=framework,
        migration_checklist=checklist,
        migration_status=status,
    )


@app.get(
    "/report/{snippet_id}",
    summary="Full migration report combining analysis and migration",
    tags=["Reports"],
)
async def get_report(snippet_id: str):
    record = storage.get(snippet_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"snippet_id '{snippet_id}' not found")
    return report_assembler.assemble(snippet_id, record)


@app.get(
    "/patterns",
    summary="List all detectable anti-patterns",
    tags=["Reference"],
)
async def list_patterns():
    return {"patterns": ANTI_PATTERNS}
