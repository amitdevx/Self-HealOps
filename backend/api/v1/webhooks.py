from fastapi import APIRouter
from backend.schemas.webhook import WebhookPayload
from backend.workers.worker import process_incident
import uuid

router = APIRouter()

@router.post("/github", status_code=202)
async def github_webhook(payload: WebhookPayload):
    # This integrates with the Event Listener logic in Phase 10
    if payload.workflow_run.get("conclusion") == "failure":
        incident_id = str(uuid.uuid4())
        # Pass to celery for async background processing
        process_incident.delay(incident_id=incident_id, evidence=str(payload.workflow_run))
        return {"status": "accepted", "message": "Failure event received, triggering incident creation.", "incident_id": incident_id}
    return {"status": "ignored", "message": "Event not related to failure."}
