from pydantic import BaseModel
import uuid
from datetime import datetime

class ValidationBase(BaseModel):
    incident_id: uuid.UUID
    build_passed: bool = False
    tests_passed: bool = False
    security_passed: bool = False
    deployment_passed: bool = False

class ValidationCreate(ValidationBase):
    pass

class ValidationUpdate(ValidationBase):
    pass

class ValidationRead(ValidationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
