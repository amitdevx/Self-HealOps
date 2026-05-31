from pydantic import BaseModel, Field

class ClassificationResult(BaseModel):
    failure_category: str = Field(description="One of: DEPENDENCY_FAILURE, BUILD_FAILURE, TEST_FAILURE, CONFIGURATION_FAILURE, INFRASTRUCTURE_FAILURE, DEPLOYMENT_FAILURE, SECURITY_FAILURE, UNKNOWN_FAILURE")

class RootCauseResult(BaseModel):
    primary_root_cause: str = Field(description="The primary reason for the failure")
    contributing_factors: list[str] = Field(description="List of contributing factors")
    confidence: float = Field(description="Confidence score between 0.0 and 100.0")
    recommended_remediation: str = Field(description="High-level suggested fix")

from typing import Literal

class ActionModel(BaseModel):
    action_type: Literal["ADD_DEPENDENCY", "CREATE_PULL_REQUEST", "RESTART_POD", "ROLLBACK_DEPLOYMENT", "SCALE_DEPLOYMENT"] = Field(description="The specific action to execute.")
    payload: dict = Field(description="Action specific arguments (e.g., {'dependency': 'requests'})")

class RemediationPlanResult(BaseModel):
    actions: list[ActionModel] = Field(description="List of structured actions to execute.")

class SafetyValidationResult(BaseModel):
    is_safe: bool = Field(description="True if the plan is completely safe to execute autonomously")
    reason: str = Field(description="Explanation of why it is safe or unsafe")

class ExecutionResult(BaseModel):
    success: bool = Field(description="True if execution succeeded")
    logs: str = Field(description="Execution logs")

class ValidationResult(BaseModel):
    is_resolved: bool = Field(description="True if the incident is fully resolved")
    details: str = Field(description="Details of the validation")

class LearningResult(BaseModel):
    pattern_extracted: bool = Field(description="True if a reusable pattern was saved")
    signature: str = Field(description="The failure signature")

class IncidentAnalysis(BaseModel):
    classification: ClassificationResult = Field(description="The failure classification")
    root_cause: RootCauseResult = Field(description="The root cause analysis")
    remediation_plan: RemediationPlanResult = Field(description="The planned remediation actions")

class BatchAnalysisResult(BaseModel):
    incidents: dict[str, IncidentAnalysis] = Field(description="Dictionary mapping incident IDs to their full analysis.")

