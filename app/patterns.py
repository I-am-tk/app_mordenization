ANTI_PATTERNS = [
    {
        "name": "GOD_CLASS",
        "description": "Single class or module doing too many unrelated things — should be split into focused units.",
    },
    {
        "name": "HARDCODED_CONFIG",
        "description": "Configuration values (URLs, IPs, credentials) baked directly into source code instead of env vars.",
    },
    {
        "name": "MAGIC_NUMBER",
        "description": "Unexplained numeric or string literals used in logic without a named constant.",
    },
    {
        "name": "TIGHT_COUPLING",
        "description": "Components directly instantiating or calling each other, making them impossible to test or replace independently.",
    },
    {
        "name": "NO_ERROR_HANDLING",
        "description": "Missing try/catch blocks, silent error suppression (On Error Resume Next), or empty catch blocks.",
    },
    {
        "name": "RAW_SQL",
        "description": "Unparameterised SQL queries built by string concatenation — vulnerable to injection and hard to maintain.",
    },
    {
        "name": "DEAD_CODE",
        "description": "Unreachable or never-called code blocks that add noise and maintenance burden.",
    },
]
