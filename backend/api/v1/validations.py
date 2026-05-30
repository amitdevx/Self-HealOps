from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.dependencies import get_db, get_current_active_user, RoleChecker
from backend.schemas.validation import ValidationCreate, ValidationRead, ValidationUpdate
from backend.models.validation import Validation
from backend.database.repository import BaseRepository
from backend.models.user import User
import uuid

router = APIRouter()
validation_repo = BaseRepository[Validation, ValidationCreate, ValidationUpdate](Validation)
allow_write = RoleChecker(["ADMIN", "ENGINEER", "AGENT"])

@router.post("/", response_model=ValidationRead, status_code=201)
async def create_validation(
    validation_in: ValidationCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_write)
):
    return await validation_repo.create(db, obj_in=validation_in)
