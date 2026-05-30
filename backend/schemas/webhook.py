from pydantic import BaseModel

class WebhookPayload(BaseModel):
    workflow_run: dict
