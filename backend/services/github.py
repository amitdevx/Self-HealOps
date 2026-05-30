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
        try:
            run = repo.get_workflow_run(run_id)
            return run.logs_url
        except Exception as e:
            return f"Failed to fetch logs for run {run_id}: {str(e)}"

    def get_recent_commits(self, repo_name: str, branch: str = "main", limit: int = 10):
        repo = self.get_repo(repo_name)
        commits = repo.get_commits(sha=branch)
        return [{"sha": c.sha, "message": c.commit.message} for c in commits[:limit]]

    def update_file_content(self, repo_name: str, file_path: str, content: str, commit_message: str, branch: str):
        repo = self.get_repo(repo_name)
        try:
            repo.get_branch(branch)
        except Exception:
            self.create_branch(repo_name, "main", branch)
            
        try:
            contents = repo.get_contents(file_path, ref=branch)
            if type(contents) is list:
                contents = contents[0]
            repo.update_file(contents.path, commit_message, content, contents.sha, branch=branch)
        except Exception:
            repo.create_file(file_path, commit_message, content, branch=branch)

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
