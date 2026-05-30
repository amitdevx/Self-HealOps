from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.dependencies import get_db, get_current_active_user, RoleChecker
from backend.schemas.action import ActionCreate, ActionRead, ActionUpdate
from backend.models.action import Action
from backend.database.repository import BaseRepository
from backend.models.user import User
import uuid

router = APIRouter()
action_repo = BaseRepository[Action, ActionCreate, ActionUpdate](Action)
allow_write = RoleChecker(["ADMIN", "ENGINEER", "AGENT"])

@router.post("/", response_model=ActionRead, status_code=201)
async def create_action(
    action_in: ActionCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_write)
):
    return await action_repo.create(db, obj_in=action_in)

@router.post("/{action_id}/execute", response_model=ActionRead)
async def execute_action(
    action_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_write)
):
    action = await action_repo.get(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    from backend.services.execution_service import execution_service
    res = execution_service.execute_action(action.action_type, action.payload)
    if res:
        return await action_repo.update(db, db_obj=action, obj_in={"status": "EXECUTED"})
    else:
        raise HTTPException(status_code=500, detail="Action execution failed")
