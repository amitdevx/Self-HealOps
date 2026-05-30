from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from backend.database.base import Base, TimestampMixin
import uuid

class Validation(Base, TimestampMixin):
    __tablename__ = "validations"

    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False)
    build_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    tests_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    security_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    deployment_passed: Mapped[bool] = mapped_column(Boolean, default=False)

    incident = relationship("Incident", back_populates="validations")
