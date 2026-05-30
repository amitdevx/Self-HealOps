from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Float, Integer
from backend.database.base import Base, TimestampMixin

class LearningPattern(Base, TimestampMixin):
    __tablename__ = "learning_patterns"

    failure_signature: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    resolution: Mapped[str] = mapped_column(Text, nullable=False)
    success_rate: Mapped[float] = mapped_column(Float, default=100.0)
    occurrences: Mapped[int] = mapped_column(Integer, default=1)
