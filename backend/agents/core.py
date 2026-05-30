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
        from backend.services.execution_service import execution_service
        success = True
        logs = []
        for action in actions:
            action_type = action.get("action_type")
            payload = action.get("payload", {})
            try:
                res = execution_service.execute_action(action_type, payload)
                logs.append(f"Action {action_type} executed: {res}")
                if not res:
                    success = False
            except Exception as e:
                logs.append(f"Error executing {action_type}: {str(e)}")
                success = False
        return ExecutionResult(success=success, logs="\n".join(logs))

    async def validate_resolution(self, incident_id: str) -> ValidationResult:
        from backend.services.github import github_service
        try:
            repo = github_service.get_repo("amitdevx/Self-HealOps")
            runs = repo.get_workflow_runs()
            if runs.totalCount > 0:
                latest_run = runs[0]
                is_resolved = (latest_run.conclusion == "success")
                return ValidationResult(is_resolved=is_resolved, details=f"CI conclusion: {latest_run.conclusion}")
            return ValidationResult(is_resolved=False, details="No workflow runs found")
        except Exception as e:
            return ValidationResult(is_resolved=False, details=str(e))

    async def extract_learning(self, incident_data: str) -> LearningResult:
        prompt = f"Extract a reusable learning pattern and unique signature from the following incident and resolution data:\n{incident_data}"
        return await nim_service.generate_structured_output(prompt, LearningResult)

agent_system = AgentSystem()
