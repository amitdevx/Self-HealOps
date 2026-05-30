from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.dependencies import get_db, get_current_active_user, RoleChecker
from backend.schemas.incident import IncidentCreate, IncidentRead, IncidentUpdate
from backend.models.incident import Incident
from backend.database.repository import BaseRepository
from backend.models.user import User
import uuid

router = APIRouter()
incident_repo = BaseRepository[Incident, IncidentCreate, IncidentUpdate](Incident)
allow_write = RoleChecker(["ADMIN", "ENGINEER", "AGENT"])

@router.post("/", response_model=IncidentRead, status_code=201)
async def create_incident(
    incident_in: IncidentCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_write)
):
    return await incident_repo.create(db, obj_in=incident_in)

@router.get("/", response_model=list[IncidentRead])
async def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await incident_repo.get_all(db, skip=skip, limit=limit)

@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    incident = await incident_repo.get(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.post("/{incident_id}/retry", response_model=IncidentRead)
async def retry_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_write)
):
    incident = await incident_repo.get(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident = await incident_repo.update(db, db_obj=incident, obj_in={"status": "RETRY", "retry_count": incident.retry_count + 1})
    return incident

@router.post("/{incident_id}/escalate", response_model=IncidentRead)
async def escalate_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_write)
):
    incident = await incident_repo.get(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident = await incident_repo.update(db, db_obj=incident, obj_in={"status": "ESCALATED"})
    return incident
