import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.risk_engine import assess


def test_hardcoded_credentials_critical():
    code = "conn.Open \"Provider=SQLOLEDB;Server=192.168.1.10;Database=LoanDB;UID=sa;PWD=Admin123\""
    risk, reasons = assess(code)
    assert risk == "CRITICAL"
    assert "HARDCODED_CREDENTIALS" in reasons


def test_raw_sql_high():
    code = "rs.Open \"SELECT * FROM Loans WHERE Status = 'PENDING'\", conn"
    risk, reasons = assess(code)
    assert risk in ("CRITICAL", "HIGH")
    assert "RAW_SQL_DETECTED" in reasons


def test_on_error_resume_next_medium():
    code = "On Error Resume Next\ncustID = CInt(inputID)"
    risk, reasons = assess(code)
    assert risk == "MEDIUM"
    assert "NO_ERROR_HANDLING" in reasons


def test_simple_logic_low():
    code = "x = 1 + 2\nprint(x)"
    risk, reasons = assess(code)
    assert risk == "LOW"
    assert "SIMPLE_LOGIC_NO_EXTERNAL_DEPS" in reasons


def test_multiple_reasons_returns_highest():
    # Has both hardcoded creds AND raw SQL — CRITICAL wins
    code = "PWD=Admin123\nSELECT * FROM users"
    risk, reasons = assess(code)
    assert risk == "CRITICAL"
    assert "HARDCODED_CREDENTIALS" in reasons
    assert "RAW_SQL_DETECTED" in reasons
