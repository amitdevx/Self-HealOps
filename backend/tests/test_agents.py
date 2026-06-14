"""Tests for AI agent system."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
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


class TestAgentSystem:
    """Test the AgentSystem orchestrator."""

    @pytest.fixture
    def agent(self):
        # Patch nim_service at the module level where it's used in core.py
        with patch("backend.agents.core.nim_service") as mock_nim:
            from backend.agents.core import AgentSystem
            system = AgentSystem()
            yield system, mock_nim

    @pytest.mark.asyncio
    async def test_classify_failure(self, agent):
        system, mock_nim = agent
        expected = ClassificationResult(failure_category="DEPENDENCY_FAILURE")
        mock_nim.generate_structured_output = AsyncMock(return_value=expected)
        result = await system.classify_failure("ModuleNotFoundError: No module named 'requests'")
        assert result.failure_category == "DEPENDENCY_FAILURE"
        mock_nim.generate_structured_output.assert_called_once()

    @pytest.mark.asyncio
    async def test_classify_failure_build(self, agent):
        system, mock_nim = agent
        expected = ClassificationResult(failure_category="BUILD_FAILURE")
        mock_nim.generate_structured_output = AsyncMock(return_value=expected)
        result = await system.classify_failure("gcc: error: compilation failed")
        assert result.failure_category == "BUILD_FAILURE"

    @pytest.mark.asyncio
    async def test_analyze_root_cause(self, agent):
        system, mock_nim = agent
        expected = RootCauseResult(
            primary_root_cause="Missing 'requests' package in requirements.txt",
            contributing_factors=["No lock file"],
            confidence=95.0,
            recommended_remediation="Add requests to requirements.txt",
        )
        mock_nim.generate_structured_output = AsyncMock(return_value=expected)
        result = await system.analyze_root_cause("ERROR: ModuleNotFoundError")
        assert result.confidence == 95.0
        assert "requests" in result.primary_root_cause
        assert len(result.contributing_factors) == 1

    @pytest.mark.asyncio
    async def test_analyze_root_cause_truncates_long_input(self, agent):
        """The core.py truncates error lines to last 5000 chars before building the prompt."""
        system, mock_nim = agent
        expected = RootCauseResult(
            primary_root_cause="test",
            contributing_factors=[],
            confidence=50.0,
            recommended_remediation="fix",
        )
        mock_nim.generate_structured_output = AsyncMock(return_value=expected)
        # Generate input with many ERROR lines to trigger error-line extraction & truncation
        long_input = "ERROR: something happened here\n" * 500
        result = await system.analyze_root_cause(long_input)
        assert result is not None
        # Verify the prompt passed to NIM was truncated (error lines capped at 5000 chars)
        call_args = mock_nim.generate_structured_output.call_args
        prompt = call_args[0][0]
        # The ROOT_CAUSE_PROMPT template adds some text, but the context portion is <= 5000
        # Total prompt should be reasonably bounded
        assert len(prompt) < 6000

    @pytest.mark.asyncio
    async def test_analyze_root_cause_no_error_lines_uses_raw_context(self, agent):
        """When no ERROR/FATAL/EXCEPTION lines exist, it uses the raw context truncated to 5000."""
        system, mock_nim = agent
        expected = RootCauseResult(
            primary_root_cause="unknown",
            contributing_factors=[],
            confidence=10.0,
            recommended_remediation="investigate",
        )
        mock_nim.generate_structured_output = AsyncMock(return_value=expected)
        # No ERROR/FATAL/EXCEPTION keywords, so raw context is used
        plain_input = "some info log\n" * 1000
        result = await system.analyze_root_cause(plain_input)
        assert result is not None
        call_args = mock_nim.generate_structured_output.call_args
        prompt = call_args[0][0]
        # Context should be truncated to last 5000 chars of raw input
        assert len(prompt) < 6000

    @pytest.mark.asyncio
    async def test_plan_remediation(self, agent):
        system, mock_nim = agent
        expected = RemediationPlanResult(
            actions=[ActionModel(action_type="ADD_DEPENDENCY", payload={"dependency": "requests"})]
        )
        mock_nim.generate_structured_output = AsyncMock(return_value=expected)
        result = await system.plan_remediation("Missing dependency: requests")
        assert len(result.actions) == 1
        assert result.actions[0].action_type == "ADD_DEPENDENCY"

    @pytest.mark.asyncio
    async def test_plan_remediation_multiple_actions(self, agent):
        system, mock_nim = agent
        expected = RemediationPlanResult(
            actions=[
                ActionModel(action_type="ADD_DEPENDENCY", payload={"dependency": "flask"}),
                ActionModel(action_type="RESTART_POD", payload={"pod_name": "web-1"}),
            ]
        )
        mock_nim.generate_structured_output = AsyncMock(return_value=expected)
        result = await system.plan_remediation("Missing dependency and pod crash")
        assert len(result.actions) == 2

    @pytest.mark.asyncio
    async def test_validate_safety_safe_plan(self, agent):
        system, mock_nim = agent
        expected = SafetyValidationResult(is_safe=True, reason="Plan contains only allowed actions")
        mock_nim.generate_structured_output = AsyncMock(return_value=expected)
        result = await system.validate_safety('[{"action_type": "ADD_DEPENDENCY"}]')
        assert result.is_safe is True

    @pytest.mark.asyncio
    async def test_validate_safety_unsafe_plan(self, agent):
        system, mock_nim = agent
        expected = SafetyValidationResult(is_safe=False, reason="Plan contains destructive action")
        mock_nim.generate_structured_output = AsyncMock(return_value=expected)
        result = await system.validate_safety('[{"action_type": "DELETE_DATABASE"}]')
        assert result.is_safe is False
        assert "destructive" in result.reason.lower()

    @pytest.mark.asyncio
    async def test_execute_plan_success(self, agent):
        system, _ = agent
        actions = [ActionModel(action_type="ADD_DEPENDENCY", payload={"dependency": "requests"})]
        with patch("backend.services.execution_service.execution_service") as mock_exec:
            mock_exec.execute_action.return_value = True
            result = await system.execute_plan(actions)
            assert result.success is True
            assert "ADD_DEPENDENCY" in result.logs

    @pytest.mark.asyncio
    async def test_execute_plan_failure(self, agent):
        system, _ = agent
        actions = [ActionModel(action_type="ADD_DEPENDENCY", payload={"dependency": "bad-pkg"})]
        with patch("backend.services.execution_service.execution_service") as mock_exec:
            mock_exec.execute_action.return_value = False
            result = await system.execute_plan(actions)
            assert result.success is False

    @pytest.mark.asyncio
    async def test_execute_plan_exception(self, agent):
        system, _ = agent
        actions = [ActionModel(action_type="RESTART_POD", payload={"pod_name": "test"})]
        with patch("backend.services.execution_service.execution_service") as mock_exec:
            mock_exec.execute_action.side_effect = PermissionError("Blocked")
            result = await system.execute_plan(actions)
            assert result.success is False
            assert "Error" in result.logs

    @pytest.mark.asyncio
    async def test_execute_plan_partial_failure(self, agent):
        """If one action fails and another succeeds, overall should be failure."""
        system, _ = agent
        actions = [
            ActionModel(action_type="ADD_DEPENDENCY", payload={"dependency": "requests"}),
            ActionModel(action_type="RESTART_POD", payload={"pod_name": "web"}),
        ]
        with patch("backend.services.execution_service.execution_service") as mock_exec:
            mock_exec.execute_action.side_effect = [True, False]
            result = await system.execute_plan(actions)
            assert result.success is False
            assert "ADD_DEPENDENCY" in result.logs
            assert "RESTART_POD" in result.logs

    @pytest.mark.asyncio
    async def test_execute_plan_empty_actions(self, agent):
        """Executing an empty plan should succeed."""
        system, _ = agent
        result = await system.execute_plan([])
        assert result.success is True
        assert result.logs == ""

    @pytest.mark.asyncio
    async def test_validate_resolution_success(self, agent):
        system, _ = agent
        mock_run = MagicMock()
        mock_run.conclusion = "success"
        mock_runs = MagicMock()
        mock_runs.totalCount = 1
        mock_runs.__getitem__ = MagicMock(return_value=mock_run)
        mock_repo = MagicMock()
        mock_repo.get_workflow_runs.return_value = mock_runs

        with patch("backend.services.github.github_service") as mock_gh:
            mock_gh.get_repo.return_value = mock_repo
            with patch("backend.core.config.settings") as mock_settings:
                mock_settings.GITHUB_REPO = "owner/repo"
                result = await system.validate_resolution("incident-1")
                assert result.is_resolved is True

    @pytest.mark.asyncio
    async def test_validate_resolution_failure(self, agent):
        system, _ = agent
        mock_run = MagicMock()
        mock_run.conclusion = "failure"
        mock_runs = MagicMock()
        mock_runs.totalCount = 1
        mock_runs.__getitem__ = MagicMock(return_value=mock_run)
        mock_repo = MagicMock()
        mock_repo.get_workflow_runs.return_value = mock_runs

        with patch("backend.services.github.github_service") as mock_gh:
            mock_gh.get_repo.return_value = mock_repo
            with patch("backend.core.config.settings") as mock_settings:
                mock_settings.GITHUB_REPO = "owner/repo"
                result = await system.validate_resolution("incident-1")
                assert result.is_resolved is False

    @pytest.mark.asyncio
    async def test_validate_resolution_no_runs(self, agent):
        system, _ = agent
        mock_runs = MagicMock()
        mock_runs.totalCount = 0
        mock_repo = MagicMock()
        mock_repo.get_workflow_runs.return_value = mock_runs

        with patch("backend.services.github.github_service") as mock_gh:
            mock_gh.get_repo.return_value = mock_repo
            with patch("backend.core.config.settings") as mock_settings:
                mock_settings.GITHUB_REPO = "owner/repo"
                result = await system.validate_resolution("incident-1")
                assert result.is_resolved is False
                assert "No workflow runs found" in result.details

    @pytest.mark.asyncio
    async def test_validate_resolution_exception(self, agent):
        system, _ = agent
        with patch("backend.services.github.github_service") as mock_gh:
            mock_gh.get_repo.side_effect = Exception("Connection error")
            with patch("backend.core.config.settings") as mock_settings:
                mock_settings.GITHUB_REPO = "owner/repo"
                result = await system.validate_resolution("incident-1")
                assert result.is_resolved is False
                assert "Connection error" in result.details

    @pytest.mark.asyncio
    async def test_extract_learning(self, agent):
        system, mock_nim = agent
        expected = LearningResult(pattern_extracted=True, signature="ModuleNotFoundError-requests")
        mock_nim.generate_structured_output = AsyncMock(return_value=expected)
        result = await system.extract_learning("Incident: ModuleNotFoundError fixed by adding requests")
        assert result.pattern_extracted is True
        assert "requests" in result.signature
