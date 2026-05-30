from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from backend.database.base import Base, TimestampMixin
import uuid

class Analysis(Base, TimestampMixin):
    __tablename__ = "analyses"

    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False)
    failure_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)

    incident = relationship("Incident", back_populates="analyses")
