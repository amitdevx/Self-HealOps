from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from backend.database.base import Base, TimestampMixin
import uuid

class Evidence(Base, TimestampMixin):
    __tablename__ = "evidence"

    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False, index=True) # e.g. "github", "ci_logs", "kubernetes"
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    incident = relationship("Incident", back_populates="evidence")
