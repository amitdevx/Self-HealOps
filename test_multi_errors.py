import asyncio
import uuid
import logging
from backend.workflows.graph import app as workflow_app

logging.basicConfig(level=logging.ERROR)

async def run_scenario(scenario_name: str, evidence: str):
    incident_id = str(uuid.uuid4())
    print(f"\n{'='*50}")
    print(f"Running Scenario: {scenario_name}")
    print(f"{'='*50}")
    
    initial_state = {
        "incident_id": incident_id,
        "evidence": evidence,
        "classification": None,
        "root_cause": None,
        "remediation_plan": None,
        "safety_validation": None,
        "execution_result": None,
        "validation_result": None,
        "learning_result": None,
        "retry_count": 0,
        "status": "OPEN"
    }

    final_state = await workflow_app.ainvoke(
        initial_state, 
        config={"configurable": {"thread_id": incident_id}}
    )
    
    print(f"\n--- Final State for {scenario_name} ---")
    print(f"Classification: {final_state.get('classification')}")
    print(f"Root Cause: {final_state.get('root_cause')}")
    print(f"Remediation Plan: {final_state.get('remediation_plan')}")
    print(f"Safety Validation: {final_state.get('safety_validation')}")
    print(f"Execution Result: {final_state.get('execution_result')}")
    print(f"Final Status: {final_state.get('status')}")

async def main():
    scenario_1_oom = """
Kubernetes Pod Failed
Namespace: production
Pod: selfhealops-api-5c7d8b9d-4x8k2
Reason: OOMKilled
Exit Code: 137

Logs:
[INFO] Application starting...
[INFO] Connecting to database...
[INFO] Database connected.
[ERROR] Memory allocation failed.
Fatal error: Out of memory.
    """
    
    scenario_2_deployment = """
Kubernetes Deployment Failed
Namespace: production
Deployment: frontend-webapp
Status: Rollout failed. Progress deadline exceeded.

Logs:
Warning  Unhealthy  4m2s (x25 over 9m)  kubelet  Readiness probe failed: HTTP probe failed with statuscode: 500
Warning  BackOff    4m (x15 over 9m)   kubelet  Back-off restarting failed container
    """

    scenario_3_config = """
GitHub Actions Workflow Failed: deploy-to-prod
Repository: amitdevx/OG_GROUP
Branch: main
Event: Push

Logs:
Run terraform apply -auto-approve
Error: Missing required argument
  on main.tf line 45, in resource "aws_instance" "web":
  45: resource "aws_instance" "web" {
The argument "ami" is required, but no definition was found.
Error: Process completed with exit code 1.
    """

    await run_scenario("OOMKilled Pod (INFRASTRUCTURE)", scenario_1_oom)
    await run_scenario("Failed Deployment Rollout (DEPLOYMENT)", scenario_2_deployment)
    await run_scenario("Terraform Configuration Error (CONFIGURATION)", scenario_3_config)

if __name__ == "__main__":
    asyncio.run(main())
