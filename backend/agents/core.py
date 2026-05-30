from backend.services.nim import nim_service
from backend.agents.schemas import (
    ClassificationResult, RootCauseResult, RemediationPlanResult, 
    SafetyValidationResult, ExecutionResult, ValidationResult, LearningResult
)
from backend.agents.prompts import (
    CLASSIFICATION_PROMPT, ROOT_CAUSE_PROMPT, REMEDIATION_PROMPT, SAFETY_PROMPT
)

class AgentSystem:
    async def classify_failure(self, context: str) -> ClassificationResult:
        prompt = CLASSIFICATION_PROMPT.format(context=context)
        return await nim_service.generate_structured_output(prompt, ClassificationResult)

    async def analyze_root_cause(self, context: str) -> RootCauseResult:
        prompt = ROOT_CAUSE_PROMPT.format(context=context)
        return await nim_service.generate_structured_output(prompt, RootCauseResult)

    async def plan_remediation(self, root_cause: str) -> RemediationPlanResult:
        prompt = REMEDIATION_PROMPT.format(root_cause=root_cause)
        return await nim_service.generate_structured_output(prompt, RemediationPlanResult)

    async def validate_safety(self, plan: str) -> SafetyValidationResult:
        prompt = SAFETY_PROMPT.format(plan=plan)
        return await nim_service.generate_structured_output(prompt, SafetyValidationResult)

    async def execute_plan(self, actions: list[dict]) -> ExecutionResult:
        # Stub logic to hook into GitHub/Infra services
        return ExecutionResult(success=True, logs="Mock execution success")

    async def validate_resolution(self, incident_id: str) -> ValidationResult:
        # Stub logic to check CI
        return ValidationResult(is_resolved=True, details="CI passed")

    async def extract_learning(self, incident_data: str) -> LearningResult:
        # Stub logic to store memory
        return LearningResult(pattern_extracted=True, signature="mock_signature")

agent_system = AgentSystem()
