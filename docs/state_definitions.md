# State Definitions

The SelfHealOps LangGraph orchestration relies on a strictly typed `TypedDict` called `IncidentState`.

```python
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
    status: str # OPEN, RESOLVED, ESCALATED, RETRYING
```

Each node in the graph reads from this state, performs processing, and returns a subset of this state which LangGraph automatically merges into the global state for the next node.
