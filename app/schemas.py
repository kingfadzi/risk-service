from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict


class ResilienceTier(str, Enum):
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"


class CIALevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ChangeSize(str, Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"


class ChangeType(str, Enum):
    DOC_CONFIG_ONLY = "DOC_CONFIG_ONLY"
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    MAJOR = "MAJOR"
    ARCHITECTURAL = "ARCHITECTURAL"


class Novelty(str, Enum):
    REPEAT = "REPEAT"
    VARIANT = "VARIANT"
    NEW_PATTERN = "NEW_PATTERN"


class RollbackComplexity(str, Enum):
    FEATURE_FLAG = "FEATURE_FLAG"
    SIMPLE = "SIMPLE"
    SCRIPTED_MULTI_STEP = "SCRIPTED_MULTI_STEP"
    MANUAL_COMPLEX = "MANUAL_COMPLEX"
    IRREVERSIBLE = "IRREVERSIBLE"


class TestDepth(str, Enum):
    NONE = "NONE"
    UNIT_ONLY = "UNIT_ONLY"
    UNIT_INTEGRATION = "UNIT_INTEGRATION"
    FULL = "FULL"
    FULL_PLUS_CHAOS = "FULL_PLUS_CHAOS"


class RuntimeExposure(str, Enum):
    NON_PROD = "NON_PROD"
    INTERNAL = "INTERNAL"
    LIMITED_EXTERNAL = "LIMITED_EXTERNAL"
    ALL_CUSTOMERS = "ALL_CUSTOMERS"


class ChangeInput(BaseModel):
    """Input schema for change risk scoring."""

    resilience_tier: ResilienceTier = Field(
        description="Application resilience tier (T1=most critical)"
    )
    cia_max: CIALevel = Field(
        description="Maximum CIA (Confidentiality, Integrity, Availability) rating"
    )
    change_size: ChangeSize = Field(
        description="Size of the change (XS to XL)"
    )
    change_type: ChangeType = Field(
        description="Type/nature of the change"
    )
    novelty: Novelty = Field(
        description="How novel is this change pattern"
    )
    rollback_complexity: RollbackComplexity = Field(
        description="Complexity of rolling back the change"
    )
    test_depth: TestDepth = Field(
        description="Depth of testing performed"
    )
    runtime_exposure: RuntimeExposure = Field(
        description="Runtime exposure level"
    )
    apps_sharing_codebase: int = Field(
        ge=0,
        description="Number of applications sharing this codebase"
    )
    downstream_critical_deps: int = Field(
        ge=0,
        description="Number of downstream critical dependencies"
    )

    model_config = {"use_enum_values": True}


class ScoreResponse(BaseModel):
    """Response schema for change risk scoring."""

    version: int = Field(description="Scorecard version")
    score: float = Field(description="Total risk score")
    band: str = Field(description="Risk band (LOW, MEDIUM, HIGH, CRITICAL)")
    feature_scores: Dict[str, float] = Field(
        description="Per-feature score breakdown"
    )
    raw_points: float = Field(
        description="Raw points before base score applied"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: int
    score_name: str


class ReloadResponse(BaseModel):
    """Config reload response."""

    status: str
    version: int
    features: list[str]
