import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    # Patch LLM calls so tests run without OPENAI_API_KEY
    mock_analysis = {
        "summary": "Connects to a database and queries loans.",
        "identified_patterns": ["HARDCODED_CONFIG", "RAW_SQL", "NO_ERROR_HANDLING"],
        "complexity_score": 6,
        "language_detected": "VB6",
    }
    with patch("app.analyser.analyse", return_value=mock_analysis), \
         patch("app.code_generator.generate", return_value="# modernised code here\nprint('done')"):
        from app.main import app
        yield TestClient(app)


VB6_SNIPPET = """
Dim conn As New ADODB.Connection
conn.Open "Provider=SQLOLEDB;Server=192.168.1.10;Database=LoanDB;UID=sa;PWD=Admin123"
Dim rs As New ADODB.Recordset
rs.Open "SELECT * FROM Loans WHERE Status = 'PENDING'", conn
"""


def test_analyze_returns_200_with_snippet_id(client):
    resp = client.post("/analyze", json={
        "language": "VB6",
        "code_snippet": VB6_SNIPPET,
        "module_name": "LoanProcessor",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "snippet_id" in data
    assert data["risk_level"] == "CRITICAL"
    assert "HARDCODED_CREDENTIALS" in data["risk_reasons"]


def test_analyze_missing_code_snippet_returns_422(client):
    resp = client.post("/analyze", json={
        "language": "VB6",
        "module_name": "LoanProcessor",
    })
    assert resp.status_code == 422


def test_migrate_returns_modernized_code(client):
    # First analyze
    resp = client.post("/analyze", json={
        "language": "VB6",
        "code_snippet": VB6_SNIPPET,
        "module_name": "LoanProcessor",
    })
    snippet_id = resp.json()["snippet_id"]

    # Then migrate
    resp = client.post(f"/migrate/{snippet_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "modernized_code" in data
    assert data["migration_status"] == "BLOCKED"  # CRITICAL → BLOCKED
    assert any("hardcoded" in t.lower() or "connection" in t.lower() for t in data["migration_checklist"])


def test_migrate_unknown_snippet_returns_404(client):
    resp = client.post("/migrate/nonexistent-id")
    assert resp.status_code == 404


def test_report_combines_analysis_and_migration(client):
    resp = client.post("/analyze", json={
        "language": "VB6",
        "code_snippet": VB6_SNIPPET,
        "module_name": "LoanProcessor",
    })
    snippet_id = resp.json()["snippet_id"]
    client.post(f"/migrate/{snippet_id}")

    resp = client.get(f"/report/{snippet_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "analysis" in data
    assert "risk_assessment" in data
    assert data["risk_assessment"]["risk_level"] == "CRITICAL"


def test_patterns_returns_all_antipatterns(client):
    resp = client.get("/patterns")
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()["patterns"]]
    for expected in ["GOD_CLASS", "RAW_SQL", "NO_ERROR_HANDLING", "MAGIC_NUMBER"]:
        assert expected in names
