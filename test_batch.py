import asyncio
import json
import logging
from backend.agents.core import agent_system

logging.basicConfig(level=logging.ERROR)

async def test_batch():
    batch_input = """
Incident 1 (OOMKilled):
Kubernetes Pod Failed
Namespace: production
Pod: selfhealops-api-5c7d8b9d-4x8k2
Reason: OOMKilled
Exit Code: 137

Incident 2 (HTTP 500 Readiness Probe):
Kubernetes Deployment Failed
Namespace: production
Deployment: frontend-webapp
Status: Rollout failed. Progress deadline exceeded.
Logs: Readiness probe failed: HTTP probe failed with statuscode: 500

Incident 3 (Missing Terraform AMI):
GitHub Actions Workflow Failed: deploy-to-prod
Logs:
Error: Missing required argument
  on main.tf line 45, in resource "aws_instance" "web":
The argument "ami" is required, but no definition was found.
    """
    
    print("Sending batch request to NIM API...")
    try:
        batch_result = await agent_system.batch_analyze(batch_input)
        print("\nBatch Analysis Successful!\n")
        print(json.dumps(batch_result.model_dump(), indent=2))
    except Exception as e:
        print(f"\nBatch Analysis Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_batch())
