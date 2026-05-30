from pydantic import BaseModel
import uuid
from datetime import datetime

class IncidentBase(BaseModel):
    repository: str
    branch: str
    pipeline_id: str
    severity: str = "unknown"
    status: str = "OPEN"
    retry_count: int = 0

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    severity: str | None = None
    status: str | None = None
    retry_count: int | None = None

class IncidentRead(IncidentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
