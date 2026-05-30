from pydantic import BaseModel
from typing import Any
import uuid
from datetime import datetime

class ActionBase(BaseModel):
    incident_id: uuid.UUID
    action_type: str
    payload: dict[str, Any]
    status: str = "PENDING"

class ActionCreate(ActionBase):
    pass

class ActionUpdate(BaseModel):
    status: str | None = None
    executed_at: datetime | None = None

class ActionRead(ActionBase):
    id: uuid.UUID
    executed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
