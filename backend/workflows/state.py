from typing import TypedDict, Annotated, Sequence
import operator
from backend.agents.schemas import (
    ClassificationResult, RootCauseResult, RemediationPlanResult, 
    SafetyValidationResult, ExecutionResult, ValidationResult, LearningResult
)

class IncidentState(TypedDict):
    incident_id: str
    evidence: str
    classification: ClassificationResult | None
    root_cause: RootCauseResult | None
    remediation_plan: RemediationPlanResult | None
    safety_validation: SafetyValidationResult | None
    execution_result: ExecutionResult | None
    validation_result: ValidationResult | None
    learning_result: LearningResult | None
    retry_count: int
    status: str # OPEN, RESOLVED, ESCALATED
