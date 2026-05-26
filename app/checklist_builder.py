_REASON_TASKS: dict[str, str] = {
    "HARDCODED_CREDENTIALS": (
        "Replace hardcoded DB connection string / credentials with environment variables"
    ),
    "RAW_SQL_DETECTED": (
        "Replace raw SQL SELECT/INSERT/UPDATE/DELETE with ORM-based parameterised query"
    ),
    "NO_ERROR_HANDLING": (
        "Add try-catch / exception handling around DB operations and external service calls"
    ),
}

_PATTERN_TASKS: dict[str, str] = {
    "GOD_CLASS": "Refactor God Class into smaller single-responsibility modules",
    "HARDCODED_CONFIG": "Extract hardcoded configuration values to environment variables or a config file",
    "MAGIC_NUMBER": "Replace magic numbers with named constants",
    "TIGHT_COUPLING": "Introduce interfaces or dependency injection to decouple components",
    "NO_ERROR_HANDLING": "Add structured error handling and logging",
    "RAW_SQL": "Replace inline SQL strings with parameterised ORM queries",
    "DEAD_CODE": "Remove identified dead / unreachable code blocks",
}


def build(module_name: str, risk_reasons: list[str], patterns: list[str]) -> list[str]:
    """Build an actionable migration checklist from risk reasons and detected patterns."""
    tasks: list[str] = []
    seen: set[str] = set()

    for reason in risk_reasons:
        task = _REASON_TASKS.get(reason)
        if task and task not in seen:
            tasks.append(task)
            seen.add(task)

    for pattern in patterns:
        task = _PATTERN_TASKS.get(pattern)
        if task and task not in seen:
            tasks.append(task)
            seen.add(task)

    tasks.append(f"Add unit test for [{module_name}] covering edge cases and error paths")
    tasks.append("Review all external dependencies and update to current stable versions")

    return tasks
