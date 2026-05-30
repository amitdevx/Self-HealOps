import pytest
from unittest.mock import patch, AsyncMock
from backend.workflows.graph import app
from backend.workflows.state import IncidentState

@pytest.mark.asyncio
async def test_workflow_execution():
    initial_state = IncidentState(
        incident_id="test-123",
        evidence="module not found error in production",
        classification=None,
        root_cause=None,
        remediation_plan=None,
        safety_validation=None,
        execution_result=None,
        validation_result=None,
        learning_result=None,
        retry_count=0,
        status="OPEN"
    )

    with patch("backend.workflows.graph.agent_system") as mock_agent:
        class DummyRC:
            primary_root_cause = "missing dependency"
        
        class DummyPlan:
            actions = [{"action_type": "ADD_DEPENDENCY", "payload": {"dependency": "requests"}}]
            
        class DummySafety:
            is_safe = True
            
        class DummyValidation:
            is_resolved = True
            
        mock_agent.classify_failure = AsyncMock(return_value="code_issue")
        mock_agent.analyze_root_cause = AsyncMock(return_value=DummyRC())
        mock_agent.plan_remediation = AsyncMock(return_value=DummyPlan())
        mock_agent.validate_safety = AsyncMock(return_value=DummySafety())
        mock_agent.execute_plan = AsyncMock(return_value=None)
        mock_agent.validate_resolution = AsyncMock(return_value=DummyValidation())
        mock_agent.extract_learning = AsyncMock(return_value=None)
        
        with patch("backend.services.learning.learning_service.find_match", new_callable=AsyncMock) as mock_find_match:
            mock_find_match.return_value = None
            
            final_state = await app.ainvoke(initial_state)
            
            assert final_state["status"] == "RESOLVED"
            mock_agent.classify_failure.assert_called_once()
            mock_agent.execute_plan.assert_called_once()
