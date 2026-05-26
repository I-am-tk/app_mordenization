from typing import Any


def assemble(snippet_id: str, record: dict[str, Any]) -> dict[str, Any]:
    """Merge stored analysis + migration data into a full report dict."""
    return {
        "snippet_id": snippet_id,
        "original_language": record["language"],
        "analysis": {
            "summary": record["summary"],
            "patterns": record["identified_patterns"],
            "complexity": record["complexity_score"],
        },
        "risk_assessment": {
            "risk_level": record["risk_level"],
            "risk_reasons": record["risk_reasons"],
        },
        "modernized_code": record.get("modernized_code"),
        "migration_checklist": record.get("migration_checklist", []),
        "target_framework": record.get("target_framework"),
        "migration_status": record.get("migration_status"),
    }
