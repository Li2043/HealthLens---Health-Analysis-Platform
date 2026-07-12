from typing import Literal, Optional

from pydantic import BaseModel, Field

MoodValue = Literal["anxious", "stressed", "low", "calm", "unknown"]
SleepQualityValue = Literal["good", "poor", "unknown"]
ExtractionConfidence = Literal["high", "medium", "low"]
MeasurementStatus = Literal["absent", "partial", "complete", "ambiguous"]
RiskLevel = Literal["low", "moderate", "high", "emergency"]
EscalationLevel = Literal["self_care", "routine", "urgent", "emergency"]
TriageTier = Literal["low", "moderate", "high", "emergency"]


Language = Literal["en", "zh"]
AnalysisMode = Literal["mock", "ai"]


class HealthInputRequest(BaseModel):
    text: str = Field(..., description="Free-text health input (demo/sample only)")
    language: Language = Field(default="en", description="Response language: en or zh")
    mode: AnalysisMode = Field(
        default="mock",
        description="mock = rules adjudicate risk; ai = AI adjudicates, rules safety net",
    )


class FieldEvidence(BaseModel):
    field: str
    value: Optional[str] = None
    evidence: Optional[str] = None
    status: MeasurementStatus


class StructuredHealthInput(BaseModel):
    heart_rate: Optional[int] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    mood: Optional[MoodValue] = None
    sleep_quality: Optional[SleepQualityValue] = None
    symptoms: list[str] = Field(default_factory=list)
    extraction_confidence: ExtractionConfidence = "low"
    missing_or_ambiguous_fields: list[str] = Field(default_factory=list)
    extraction_notes: Optional[str] = None
    extraction_evidence: list[FieldEvidence] = Field(default_factory=list)


class RiskResult(BaseModel):
    risk_level: RiskLevel
    flags: list[str]
    rule_explanation: str


class RiskAdjudication(BaseModel):
    mode: AnalysisMode
    ai_risk_level: Optional[RiskLevel] = None
    rule_risk_level: RiskLevel
    final_risk_level: RiskLevel
    adjudicated_by: Literal[
        "rules", "ai", "ai_with_rule_override", "ai_with_emergency_override"
    ]
    rule_override_applied: bool = False
    override_reason: Optional[str] = None


class SafetyCheck(BaseModel):
    contains_disclaimer: bool
    contains_diagnostic_language: bool
    contains_medication_advice: bool
    passed: bool


class EscalationResult(BaseModel):
    level: EscalationLevel
    triage_tier: TriageTier
    is_emergency: bool = False
    matched_patterns: list[str] = Field(default_factory=list)
    recommended_action: str


class AnalysisResponse(BaseModel):
    structured_input: StructuredHealthInput
    risk_result: RiskResult
    escalation: EscalationResult
    explanation: str
    safety_check: SafetyCheck
    extractor_provider: str
    llm_provider: str
    analysis_mode: AnalysisMode = "mock"
    risk_adjudication: Optional[RiskAdjudication] = None
    provider_warning: Optional[str] = None
