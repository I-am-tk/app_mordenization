import re

_HARDCODED_CRED = [
    re.compile(r"(?i)(PWD|Password|passwd)\s*=\s*[\"']?[^\s\"'&;]+"),
    re.compile(r"(?i)(UID=|User\s*ID=)[^\s;\"']+"),
    re.compile(r"(?i)conn.*Open\s+[\"'].*Provider="),
    re.compile(r"(?i)(connection_string|conn_str|connstr)\s*=\s*[\"']"),
    re.compile(r"(?i)Server\s*=\s*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
]

_RAW_SQL = [
    re.compile(r"(?i)\b(SELECT\s+.+\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b"),
    re.compile(r'(?i)rs\.Open\s+["\']'),
    re.compile(r'(?i)\.Execute\s*\(\s*["\']'),
    re.compile(r'(?i)ExecuteQuery\s*\('),
]

_NO_ERROR_HANDLING = [
    re.compile(r"(?i)On\s+Error\s+Resume\s+Next"),
    re.compile(r"catch\s*\(\s*\)\s*\{[\s\n]*\}"),
    re.compile(r"except\s*:\s*\n\s*pass"),
    re.compile(r"catch\s*\([^)]*\)\s*\{[\s\n]*(//[^\n]*)?\s*\}"),
]

_NO_INPUT_VALIDATION = [
    re.compile(r"(?i)Request\.(Form|QueryString|ServerVariables)\s*\("),
    re.compile(r"(?i)Request\.(Form|QueryString)\s*\["),
    re.compile(r"(?i)\$_(GET|POST|REQUEST)\s*\["),
    re.compile(r"(?i)(argv|sys\.argv|input\(\)|raw_input\(\))"),
]


def assess(code: str) -> tuple[str, list[str]]:
    """Return (risk_level, risk_reasons[]) using pure regex — no LLM."""
    reasons: list[str] = []

    if any(p.search(code) for p in _HARDCODED_CRED):
        reasons.append("HARDCODED_CREDENTIALS")

    if any(p.search(code) for p in _RAW_SQL):
        reasons.append("RAW_SQL_DETECTED")

    if any(p.search(code) for p in _NO_ERROR_HANDLING):
        reasons.append("NO_ERROR_HANDLING")

    if any(p.search(code) for p in _NO_INPUT_VALIDATION):
        reasons.append("NO_INPUT_VALIDATION")

    if "HARDCODED_CREDENTIALS" in reasons:
        return "CRITICAL", reasons
    if "RAW_SQL_DETECTED" in reasons:
        return "HIGH", reasons
    if "NO_ERROR_HANDLING" in reasons:
        return "MEDIUM", reasons
    if "NO_INPUT_VALIDATION" in reasons:
        return "MEDIUM", reasons
    return "LOW", ["SIMPLE_LOGIC_NO_EXTERNAL_DEPS"]
