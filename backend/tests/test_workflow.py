"""Tests for LangGraph workflow execution."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from backend.workflows.state import IncidentState
from backend.agents.schemas import (
    ClassificationResult,
    RootCauseResult,
    RemediationPlanResult,
    SafetyValidationResult,
    ExecutionResult,
    ValidationResult,
    LearningResult,
    ActionModel,
)


class TestIncidentState:
    """Test IncidentState TypedDict structure."""

    def test_state_creation(self):
        state = IncidentState(
            incident_id="test-123",
            evidence="test error log",
            classification=None,
            root_cause=None,
            remediation_plan=None,
            safety_validation=None,
            execution_result=None,
            validation_result=None,
            learning_result=None,
            retry_count=0,
            status="OPEN",
        )
        assert state["incident_id"] == "test-123"
        assert state["status"] == "OPEN"
        assert state["retry_count"] == 0


class TestWorkflowNodes:
    """Test individual workflow nodes in isolation."""

    @pytest.mark.asyncio
    async def test_classify_node(self):
        from backend.workflows.graph import classify_node
        state = IncidentState(
            incident_id="test-1", evidence="ModuleNotFoundError",
            classification=None, root_cause=None, remediation_plan=None,
            safety_validation=None, execution_result=None,
            validation_result=None, learning_result=None, retry_count=0, status="OPEN",
        )
        expected = ClassificationResult(failure_category="DEPENDENCY_FAILURE")
        with patch("backend.workflows.graph.agent_system") as mock_agent:
            mock_agent.classify_failure = AsyncMock(return_value=expected)
            result = await classify_node(state)
            assert result["classification"].failure_category == "DEPENDENCY_FAILURE"

    @pytest.mark.asyncio
    async def test_rca_node(self):
        from backend.workflows.graph import rca_node
        state = IncidentState(
            incident_id="test-2", evidence="ERROR: missing module",
            classification=None, root_cause=None, remediation_plan=None,
            safety_validation=None, execution_result=None,
            validation_result=None, learning_result=None, retry_count=0, status="OPEN",
        )
        expected = RootCauseResult(
            primary_root_cause="missing module", contributing_factors=[], confidence=90.0, recommended_remediation="install"
        )
        with patch("backend.workflows.graph.agent_system") as mock_agent:
            mock_agent.analyze_root_cause = AsyncMock(return_value=expected)
            result = await rca_node(state)
            assert result["root_cause"].primary_root_cause == "missing module"

    @pytest.mark.asyncio
    async def test_plan_node(self):
        from backend.workflows.graph import plan_node
        rc_result = RootCauseResult(
            primary_root_cause="missing module", contributing_factors=[], confidence=90.0, recommended_remediation="install"
        )
        state = IncidentState(
            incident_id="test-3", evidence="",
            classification=None, root_cause=rc_result, remediation_plan=None,
            safety_validation=None, execution_result=None,
            validation_result=None, learning_result=None, retry_count=0, status="OPEN",
        )
        expected = RemediationPlanResult(actions=[ActionModel(action_type="ADD_DEPENDENCY", payload={})])
        with patch("backend.workflows.graph.agent_system") as mock_agent:
            mock_agent.plan_remediation = AsyncMock(return_value=expected)
            result = await plan_node(state)
            assert len(result["remediation_plan"].actions) == 1

    @pytest.mark.asyncio
    async def test_safety_node(self):
        from backend.workflows.graph import safety_node
        plan_result = RemediationPlanResult(actions=[ActionModel(action_type="ADD_DEPENDENCY", payload={})])
        state = IncidentState(
            incident_id="test-4", evidence="",
            classification=None, root_cause=None, remediation_plan=plan_result,
            safety_validation=None, execution_result=None,
            validation_result=None, learning_result=None, retry_count=0, status="OPEN",
        )
        expected = SafetyValidationResult(is_safe=True, reason="ok")
        with patch("backend.workflows.graph.agent_system") as mock_agent:
            mock_agent.validate_safety = AsyncMock(return_value=expected)
            result = await safety_node(state)
            assert result["safety_validation"].is_safe is True

    @pytest.mark.asyncio
    async def test_execute_node(self):
        from backend.workflows.graph import execute_node
        plan_result = RemediationPlanResult(actions=[ActionModel(action_type="ADD_DEPENDENCY", payload={})])
        state = IncidentState(
            incident_id="test-5", evidence="",
            classification=None, root_cause=None, remediation_plan=plan_result,
            safety_validation=None, execution_result=None,
            validation_result=None, learning_result=None, retry_count=0, status="OPEN",
        )
        expected = ExecutionResult(success=True, logs="done")
        with patch("backend.workflows.graph.agent_system") as mock_agent:
            mock_agent.execute_plan = AsyncMock(return_value=expected)
            result = await execute_node(state)
            assert result["execution_result"].success is True

    @pytest.mark.asyncio
    async def test_validate_node(self):
        from backend.workflows.graph import validate_node
        state = IncidentState(
            incident_id="test-6", evidence="",
            classification=None, root_cause=None, remediation_plan=None,
            safety_validation=None, execution_result=None,
            validation_result=None, learning_result=None, retry_count=0, status="OPEN",
        )
        expected = ValidationResult(is_resolved=True, details="fixed")
        with patch("backend.workflows.graph.agent_system") as mock_agent:
            mock_agent.validate_resolution = AsyncMock(return_value=expected)
            result = await validate_node(state)
            assert result["validation_result"].is_resolved is True

    @pytest.mark.asyncio
    async def test_learn_node(self):
        from backend.workflows.graph import learn_node
        state = IncidentState(
            incident_id="test-7", evidence="test",
            classification=None, root_cause=None, remediation_plan=None,
            safety_validation=None, execution_result=None,
            validation_result=None, learning_result=None, retry_count=0, status="OPEN",
        )
        expected = LearningResult(pattern_extracted=True, signature="sig")
        with patch("backend.workflows.graph.agent_system") as mock_agent:
            mock_agent.extract_learning = AsyncMock(return_value=expected)
            result = await learn_node(state)
            assert result["learning_result"].pattern_extracted is True
            assert result["status"] == "RESOLVED"

    @pytest.mark.asyncio
    async def test_escalate_node(self):
        from backend.workflows.graph import escalate_node
        state = IncidentState(
            incident_id="test-8", evidence="",
            classification=None, root_cause=None, remediation_plan=None,
            safety_validation=None, execution_result=None,
            validation_result=None, learning_result=None, retry_count=0, status="OPEN",
        )
        result = await escalate_node(state)
        assert result["status"] == "ESCALATED"

    @pytest.mark.asyncio
    async def test_retry_node(self):
        from backend.workflows.graph import retry_node
        state = IncidentState(
            incident_id="test-9", evidence="",
            classification=None, root_cause=None, remediation_plan=None,
            safety_validation=None, execution_result=None,
            validation_result=None, learning_result=None, retry_count=1, status="OPEN",
        )
        result = await retry_node(state)
        assert result["retry_count"] == 2
        assert result["status"] == "RETRYING"


class TestWorkflowEdges:
    """Test conditional routing logic."""

    def test_safety_edge(self):
        from backend.workflows.graph import safety_edge
        state_safe = IncidentState(
            incident_id="", evidence="", classification=None, root_cause=None, remediation_plan=None,
            safety_validation=SafetyValidationResult(is_safe=True, reason="ok"),
            execution_result=None, validation_result=None, learning_result=None, retry_count=0, status="OPEN",
        )
        assert safety_edge(state_safe) == "execute"

        state_unsafe = IncidentState(
            incident_id="", evidence="", classification=None, root_cause=None, remediation_plan=None,
            safety_validation=SafetyValidationResult(is_safe=False, reason="bad"),
            execution_result=None, validation_result=None, learning_result=None, retry_count=0, status="OPEN",
        )
        assert safety_edge(state_unsafe) == "escalate"

    def test_validation_edge(self):
        from backend.workflows.graph import validation_edge
        state_resolved = IncidentState(
            incident_id="", evidence="", classification=None, root_cause=None, remediation_plan=None, safety_validation=None, execution_result=None,
            validation_result=ValidationResult(is_resolved=True, details=""),
            learning_result=None, retry_count=0, status="OPEN",
        )
        assert validation_edge(state_resolved) == "learn"

        state_retry = IncidentState(
            incident_id="", evidence="", classification=None, root_cause=None, remediation_plan=None, safety_validation=None, execution_result=None,
            validation_result=ValidationResult(is_resolved=False, details=""),
            learning_result=None, retry_count=1, status="OPEN",
        )
        assert validation_edge(state_retry) == "retry"

        state_escalate = IncidentState(
            incident_id="", evidence="", classification=None, root_cause=None, remediation_plan=None, safety_validation=None, execution_result=None,
            validation_result=ValidationResult(is_resolved=False, details=""),
            learning_result=None, retry_count=3, status="OPEN",
        )
        assert validation_edge(state_escalate) == "escalate"
