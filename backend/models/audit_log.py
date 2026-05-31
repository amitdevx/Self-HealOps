from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.types import JSON
from backend.database.base import Base, TimestampMixin
import uuid

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    agent: Mapped[str] = mapped_column(String, nullable=False, index=True)
    action: Mapped[str] = mapped_column(String, nullable=False, index=True)
    result: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)
    incident_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
