"""Tests for execution service."""
import pytest
from unittest.mock import patch, MagicMock
from backend.services.execution_service import ExecutionService, SAFE_ACTIONS, BLOCKED_ACTIONS


class TestExecutionService:
    """Test execution service safety and action logic."""

    @pytest.fixture
    def exec_svc(self):
        return ExecutionService()

    def test_blocked_action_raises_permission_error(self, exec_svc):
        for action in BLOCKED_ACTIONS:
            with pytest.raises(PermissionError, match="explicitly blocked"):
                exec_svc.execute_action(action, {})

    def test_unknown_action_returns_false(self, exec_svc):
        assert exec_svc.execute_action("UNKNOWN_ACTION", {}) is False

    def test_safe_actions_set(self):
        assert "ADD_DEPENDENCY" in SAFE_ACTIONS
        assert "CREATE_PULL_REQUEST" in SAFE_ACTIONS
        assert "RESTART_POD" in SAFE_ACTIONS

    def test_blocked_actions_set(self):
        assert "DELETE_DATABASE" in BLOCKED_ACTIONS
        assert "DELETE_REPOSITORY" in BLOCKED_ACTIONS
        assert "DESTROY_CLUSTER" in BLOCKED_ACTIONS

    @patch("backend.services.execution_service.execution_service")
    def test_add_dependency_no_dependency_param(self, mock_svc):
        svc = ExecutionService()
        result = svc._execute_add_dependency({})
        assert result is False

    @patch("subprocess.run")
    def test_restart_pod_success(self, mock_run, exec_svc):
        mock_run.return_value = MagicMock(returncode=0)
        result = exec_svc._execute_restart_pod({"pod_name": "test-pod", "namespace": "default"})
        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_restart_pod_no_pod_name(self, mock_run, exec_svc):
        result = exec_svc._execute_restart_pod({})
        assert result is False
        mock_run.assert_not_called()

    @patch("subprocess.run")
    def test_rollback_deployment_success(self, mock_run, exec_svc):
        mock_run.return_value = MagicMock(returncode=0)
        result = exec_svc._execute_rollback_deployment({"deployment": "my-app"})
        assert result is True

    @patch("subprocess.run")
    def test_rollback_deployment_no_deployment(self, mock_run, exec_svc):
        result = exec_svc._execute_rollback_deployment({})
        assert result is False

    @patch("subprocess.run")
    def test_scale_deployment_success(self, mock_run, exec_svc):
        mock_run.return_value = MagicMock(returncode=0)
        result = exec_svc._execute_scale_deployment({"deployment": "my-app", "replicas": 3})
        assert result is True

    @patch("subprocess.run")
    def test_scale_deployment_no_deployment(self, mock_run, exec_svc):
        result = exec_svc._execute_scale_deployment({})
        assert result is False
