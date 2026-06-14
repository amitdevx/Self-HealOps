"""Tests for GitHub service."""
import pytest
from unittest.mock import MagicMock, patch
from backend.services.github import GitHubService


class TestGitHubService:
    """Test GitHub service with mocked PyGithub client."""

    @pytest.fixture
    def github_svc(self):
        with patch("backend.services.github.Github") as mock_github_cls:
            mock_client = MagicMock()
            mock_github_cls.return_value = mock_client
            service = GitHubService()
            service.client = mock_client
            yield service, mock_client

    def test_get_repo(self, github_svc):
        service, mock_client = github_svc
        mock_repo = MagicMock()
        mock_client.get_repo.return_value = mock_repo
        result = service.get_repo("owner/repo")
        assert result == mock_repo
        mock_client.get_repo.assert_called_once_with("owner/repo")

    def test_get_repo_no_token(self):
        with patch("backend.services.github.settings") as mock_settings:
            mock_settings.GITHUB_TOKEN = None
            service = GitHubService()
            with pytest.raises(ValueError, match="GitHub Token not configured"):
                service.get_repo("owner/repo")

    def test_get_workflow_logs(self, github_svc):
        service, mock_client = github_svc
        mock_repo = MagicMock()
        mock_run = MagicMock()
        mock_run.logs_url = "https://github.com/logs/123.zip"
        mock_repo.get_workflow_run.return_value = mock_run
        mock_client.get_repo.return_value = mock_repo

        result = service.get_workflow_logs("owner/repo", 123)
        assert "github.com/logs" in result

    def test_get_workflow_logs_failure(self, github_svc):
        service, mock_client = github_svc
        mock_repo = MagicMock()
        mock_repo.get_workflow_run.side_effect = Exception("Not found")
        mock_client.get_repo.return_value = mock_repo

        result = service.get_workflow_logs("owner/repo", 999)
        assert "Failed to fetch logs" in result

    def test_create_pull_request(self, github_svc):
        service, mock_client = github_svc
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_pr.html_url = "https://github.com/owner/repo/pull/42"
        mock_repo.create_pull.return_value = mock_pr
        mock_client.get_repo.return_value = mock_repo

        result = service.create_pull_request("owner/repo", "Fix bug", "Details", "fix-branch")
        assert result == "https://github.com/owner/repo/pull/42"

    def test_create_branch(self, github_svc):
        service, mock_client = github_svc
        mock_repo = MagicMock()
        mock_ref = MagicMock()
        mock_ref.object.sha = "abc123"
        mock_repo.get_git_ref.return_value = mock_ref
        mock_client.get_repo.return_value = mock_repo

        result = service.create_branch("owner/repo", "main", "feature")
        assert result == "feature"
        mock_repo.create_git_ref.assert_called_once()
