import pytest
from unittest.mock import MagicMock
from backend.services.github import GitHubService

def test_github_service_mocked():
    service = GitHubService()
    service.client = MagicMock()
    mock_repo = MagicMock()
    service.client.get_repo.return_value = mock_repo
    
    # Test logs
    logs = service.get_workflow_logs("repo", 1)
    assert "Mock logs" in logs

    # Test PR
    mock_pr = MagicMock()
    mock_pr.html_url = "https://github.com/test/repo/pull/1"
    mock_repo.create_pull.return_value = mock_pr
    
    url = service.create_pull_request("repo", "title", "body", "head", "base")
    assert url == "https://github.com/test/repo/pull/1"
