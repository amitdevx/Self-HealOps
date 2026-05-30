from github import Github
from github.Repository import Repository
from backend.core.config import settings

class GitHubService:
    def __init__(self):
        self.client = Github(settings.GITHUB_TOKEN) if settings.GITHUB_TOKEN else None

    def get_repo(self, repo_name: str) -> Repository:
        if not self.client:
            raise ValueError("GitHub Token not configured")
        return self.client.get_repo(repo_name)

    def get_workflow_logs(self, repo_name: str, run_id: int) -> str:
        repo = self.get_repo(repo_name)
        # Mocking downloading logs as PyGithub requires downloading a zip and extracting
        return f"Mock logs for workflow run {run_id} showing module not found error."

    def get_recent_commits(self, repo_name: str, branch: str = "main", limit: int = 10):
        repo = self.get_repo(repo_name)
        commits = repo.get_commits(sha=branch)
        return [{"sha": c.sha, "message": c.commit.message} for c in commits[:limit]]

    def create_branch(self, repo_name: str, base_branch: str, new_branch: str):
        repo = self.get_repo(repo_name)
        base_ref = repo.get_git_ref(f"heads/{base_branch}")
        repo.create_git_ref(ref=f"refs/heads/{new_branch}", sha=base_ref.object.sha)
        return new_branch

    def create_pull_request(self, repo_name: str, title: str, body: str, head: str, base: str = "main"):
        repo = self.get_repo(repo_name)
        pr = repo.create_pull(title=title, body=body, head=head, base=base)
        return pr.html_url

github_service = GitHubService()
