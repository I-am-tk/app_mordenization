from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Language(str, Enum):
    VB6 = "VB6"
    CLASSIC_ASP = "ClassicASP"
    JAVA_EE = "JavaEE"
    COBOL = "COBOL"


class TargetFramework(str, Enum):
    PYTHON_FASTAPI = "python_fastapi"
    DOTNET8 = "dotnet8"
    NODEJS_EXPRESS = "nodejs_express"
    JAVA_SPRINGBOOT = "java_springboot"


class RiskLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class MigrationStatus(str, Enum):
    READY = "READY"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    BLOCKED = "BLOCKED"


class AnalyzeRequest(BaseModel):
    language: Language
    code_snippet: str = Field(..., min_length=1)
    module_name: str = Field(..., min_length=1)
    description: Optional[str] = None


class AnalyzeResponse(BaseModel):
    snippet_id: str
    summary: str
    identified_patterns: list[str]
    complexity_score: int
    language_detected: str
    risk_level: RiskLevel
    risk_reasons: list[str]


class MigrateResponse(BaseModel):
    snippet_id: str
    modernized_code: str
    target_framework: str
    migration_checklist: list[str]
    migration_status: MigrationStatus


class AnalysisSection(BaseModel):
    summary: str
    patterns: list[str]
    complexity: int


class RiskSection(BaseModel):
    risk_level: RiskLevel
    risk_reasons: list[str]


class ReportResponse(BaseModel):
    snippet_id: str
    original_language: str
    analysis: AnalysisSection
    risk_assessment: RiskSection
    modernized_code: Optional[str] = None
    migration_checklist: list[str] = []
    target_framework: Optional[str] = None
    migration_status: Optional[MigrationStatus] = None
