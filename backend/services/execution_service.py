import logging
from backend.core.config import settings

logger = logging.getLogger(__name__)

SAFE_ACTIONS = {
    "ADD_DEPENDENCY",
    "CREATE_PULL_REQUEST",
    "RESTART_POD",
    "ROLLBACK_DEPLOYMENT",
    "SCALE_DEPLOYMENT"
}

BLOCKED_ACTIONS = {
    "DELETE_DATABASE",
    "DELETE_REPOSITORY",
    "DESTROY_CLUSTER"
}

class ExecutionService:
    def execute_action(self, action_type: str, payload: dict) -> bool:
        if action_type in BLOCKED_ACTIONS:
            logger.error(f"Policy Violation: Attempted to execute blocked action {action_type}")
            raise PermissionError(f"Action {action_type} is explicitly blocked by policy.")
            
        if action_type not in SAFE_ACTIONS:
            logger.warning(f"Unknown action {action_type} requested.")
            return False
            
        logger.info(f"Executing allowed action: {action_type} with payload {payload}")
        
        if action_type == "ADD_DEPENDENCY":
            return self._execute_add_dependency(payload)
        elif action_type == "CREATE_PULL_REQUEST":
            return self._execute_create_pr(payload)
        elif action_type == "RESTART_POD":
            return self._execute_restart_pod(payload)
        elif action_type == "ROLLBACK_DEPLOYMENT":
            return self._execute_rollback_deployment(payload)
        elif action_type == "SCALE_DEPLOYMENT":
            return self._execute_scale_deployment(payload)
        return False
        
    def _execute_add_dependency(self, payload: dict) -> bool:
        dependency = payload.get("dependency") or payload.get("dependency_name")
        repo_name = payload.get("repository", settings.GITHUB_REPO)
        branch = payload.get("branch", "selfhealops-fix")
        if not dependency:
            return False
        from backend.services.github import github_service
        try:
            # Append locally so local processes pass tests if needed
            with open("requirements.txt", "a") as f:
                f.write(f"\n{dependency}\n")
            
            # Read and push securely
            with open("requirements.txt", "r") as f:
                content = f.read()
                
            github_service.update_file_content(
                repo_name, "requirements.txt", content, f"Add {dependency}", branch
            )
            logger.info(f"Added dependency {dependency} to requirements.txt (remotely)")
            return True
        except Exception as e:
            logger.error(f"Failed to add dependency: {e}")
            return False
        
    def _execute_create_pr(self, payload: dict) -> bool:
        from backend.services.github import github_service
        try:
            github_service.create_pull_request(
                repo_name=payload.get("repository", settings.GITHUB_REPO),
                title=payload.get("title", "Automated Remediation"),
                body=payload.get("body", "SelfHealOps automated fix"),
                head_branch=payload.get("branch", "selfhealops-fix")
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return False
        
    def _execute_restart_pod(self, payload: dict) -> bool:
        import subprocess
        namespace = payload.get("namespace", "default")
        pod_name = payload.get("pod_name")
        if not pod_name:
            return False
        res = subprocess.run(["kubectl", "delete", "pod", pod_name, "-n", namespace], capture_output=True)
        return res.returncode == 0
        
    def _execute_rollback_deployment(self, payload: dict) -> bool:
        import subprocess
        namespace = payload.get("namespace", "default")
        deployment = payload.get("deployment")
        if not deployment:
            return False
        res = subprocess.run(["kubectl", "rollout", "undo", f"deployment/{deployment}", "-n", namespace], capture_output=True)
        return res.returncode == 0
        
    def _execute_scale_deployment(self, payload: dict) -> bool:
        import subprocess
        namespace = payload.get("namespace", "default")
        deployment = payload.get("deployment")
        replicas = payload.get("replicas", 1)
        if not deployment:
            return False
        res = subprocess.run(["kubectl", "scale", f"deployment/{deployment}", f"--replicas={replicas}", "-n", namespace], capture_output=True)
        return res.returncode == 0

execution_service = ExecutionService()
