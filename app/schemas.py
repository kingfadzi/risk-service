from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict


# === QUESTIONNAIRE-BASED ENUMS ===

class DataSensitivity(str, Enum):
    """Q1: What is the most sensitive type of data your application handles?"""
    PAYMENT_CARD_DATA = "payment_card_data"
    REGULATED_PII = "regulated_pii"
    CUSTOMER_PII = "customer_pii"
    INTERNAL_BUSINESS = "internal_business"
    PUBLIC_DATA = "public_data"


class DowntimeImpact(str, Enum):
    """Q2: If this application is unavailable for 4 hours, what is the impact?"""
    REVENUE_LOSS_CRITICAL = "revenue_loss_critical"
    MAJOR_DISRUPTION = "major_disruption"
    PRODUCTIVITY_IMPACT = "productivity_impact"
    MINIMAL_IMPACT = "minimal_impact"


class IntegrityImpact(str, Enum):
    """Q3: If your application's data becomes corrupted, what is the impact?"""
    FINANCIAL_HARM = "financial_harm"
    DECISION_IMPACT = "decision_impact"
    OPERATIONAL_INEFFICIENCY = "operational_inefficiency"
    LOW_IMPACT = "low_impact"


class BreachConsequence(str, Enum):
    """Q4: If an attacker gains unauthorized access, what is the worst case?"""
    PAYMENT_EXPOSURE = "payment_exposure"
    PII_BREACH = "pii_breach"
    CUSTOMER_DATA_EXPOSURE = "customer_data_exposure"
    INTERNAL_EXPOSURE = "internal_exposure"
    PUBLIC_ONLY = "public_only"


class DisasterRecovery(str, Enum):
    """Q5: How quickly must the system be restored after total loss?"""
    FOUR_HOURS = "four_hours"
    TWENTYFOUR_HOURS = "twentyfour_hours"
    THREE_DAYS = "three_days"
    ONE_WEEK = "one_week"


class SystemDependencies(str, Enum):
    """Q6: How many other systems depend on this application?"""
    HIGH_DEPENDENCY = "high_dependency"
    MODERATE_DEPENDENCY = "moderate_dependency"
    LOW_DEPENDENCY = "low_dependency"
    STANDALONE = "standalone"


# === CMDB-BASED ENUMS ===

class ResilienceCategory(str, Enum):
    """CMDB resilience category (0=most critical, 3=least)"""
    CAT_0 = "0"
    CAT_1 = "1"
    CAT_2 = "2"
    CAT_3 = "3"


# === GIT/CI-BASED ENUMS ===

class ChangeSize(str, Enum):
    """Size of the change derived from git diff"""
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"


class TestDepth(str, Enum):
    """Test depth from CI/CD pipeline"""
    NONE = "NONE"
    UNIT_ONLY = "UNIT_ONLY"
    UNIT_INTEGRATION = "UNIT_INTEGRATION"
    FULL = "FULL"
    FULL_PLUS_CHAOS = "FULL_PLUS_CHAOS"


# === INPUT/OUTPUT MODELS ===

class ChangeInput(BaseModel):
    """Input schema for change risk scoring.

    All fields are programmatically collectible:
    - Questionnaire answers: from risk assessment wizard
    - CMDB fields: from service offering data
    - Git/CI fields: from pipeline and repository
    - Derived fields: computed from component mapping and dependency graph
    """

    # Questionnaire-based fields
    data_sensitivity: DataSensitivity = Field(
        description="Most sensitive data type handled (from questionnaire)"
    )
    downtime_impact: DowntimeImpact = Field(
        description="Business impact of 4-hour outage (from questionnaire)"
    )
    integrity_impact: IntegrityImpact = Field(
        description="Impact of data corruption (from questionnaire)"
    )
    breach_consequence: BreachConsequence = Field(
        description="Worst-case security breach scenario (from questionnaire)"
    )
    disaster_recovery: DisasterRecovery = Field(
        description="Required recovery time objective (from questionnaire)"
    )
    system_dependencies: SystemDependencies = Field(
        description="Number of dependent systems (from questionnaire)"
    )
    regulatory_count: int = Field(
        ge=0,
        le=5,
        description="Count of applicable regulatory frameworks (0-5)"
    )

    # CMDB-based fields
    resilience_category: ResilienceCategory = Field(
        description="CMDB resilience tier (0=most critical)"
    )

    # Git/CI-based fields
    change_size: ChangeSize = Field(
        description="Size of the change from git diff"
    )
    test_depth: TestDepth = Field(
        description="Test depth from CI/CD pipeline"
    )

    # Derived fields
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
