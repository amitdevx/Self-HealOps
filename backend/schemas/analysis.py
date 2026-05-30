from pydantic import BaseModel
import uuid
from datetime import datetime

class AnalysisBase(BaseModel):
    incident_id: uuid.UUID
    failure_type: str
    root_cause: str
    confidence: float
    recommendation: str

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisUpdate(BaseModel):
    confidence: float | None = None

class AnalysisRead(AnalysisBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
