from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.dependencies import get_db, get_current_active_user, RoleChecker
from backend.schemas.analysis import AnalysisCreate, AnalysisRead, AnalysisUpdate
from backend.models.analysis import Analysis
from backend.database.repository import BaseRepository
from backend.models.user import User
import uuid

router = APIRouter()
analysis_repo = BaseRepository[Analysis, AnalysisCreate, AnalysisUpdate](Analysis)
allow_write = RoleChecker(["ADMIN", "ENGINEER", "AGENT"])

@router.post("/", response_model=AnalysisRead, status_code=201)
async def create_analysis(
    analysis_in: AnalysisCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_write)
):
    return await analysis_repo.create(db, obj_in=analysis_in)

@router.get("/{analysis_id}", response_model=AnalysisRead)
async def get_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    analysis = await analysis_repo.get(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
