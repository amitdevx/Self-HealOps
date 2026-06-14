from fastapi import APIRouter, HTTPException, Request, Header
from backend.schemas.webhook import WebhookPayload
from backend.workers.worker import process_incident
from backend.core.config import settings
import uuid
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def verify_github_signature(payload_body: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature using HMAC-SHA256."""
    if not secret:
        logger.warning("GITHUB_WEBHOOK_SECRET not configured, skipping signature verification")
        return True
    if not signature:
        return False
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"), payload_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/github", status_code=202)
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(None),
):
    """Handle GitHub webhook events with signature verification."""
    body = await request.body()

    if not verify_github_signature(body, x_hub_signature_256, settings.GITHUB_WEBHOOK_SECRET):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    payload = await request.json()
    workflow_run = payload.get("workflow_run", {})

    if payload.get("action") == "completed" and workflow_run.get("conclusion") == "failure":
        incident_id = str(uuid.uuid4())
        process_incident.delay(incident_id=incident_id, evidence=str(workflow_run))
        logger.info(f"Incident created from webhook: {incident_id}")
        return {
            "status": "accepted",
            "message": "Failure event received, triggering incident creation.",
            "incident_id": incident_id,
        }
    return {"status": "ignored", "message": "Event not related to failure."}
