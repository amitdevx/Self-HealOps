from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from backend.database.base import Base, TimestampMixin, SoftDeleteMixin
import uuid

class Incident(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "incidents"

    repository: Mapped[str] = mapped_column(String, index=True, nullable=False)
    branch: Mapped[str] = mapped_column(String, nullable=False)
    pipeline_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String, default="unknown", index=True)
    status: Mapped[str] = mapped_column(String, default="OPEN", index=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    evidence = relationship("Evidence", back_populates="incident", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="incident", cascade="all, delete-orphan")
    actions = relationship("Action", back_populates="incident", cascade="all, delete-orphan")
    validations = relationship("Validation", back_populates="incident", cascade="all, delete-orphan")
