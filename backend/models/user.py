from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from backend.database.base import Base, TimestampMixin, SoftDeleteMixin

class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="VIEWER")
    is_active: Mapped[bool] = mapped_column(default=True)
