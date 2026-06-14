"""Tests for database models and repository operations."""
import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.user import User
from backend.models.incident import Incident
from backend.models.action import Action
from backend.models.analysis import Analysis
from backend.models.evidence import Evidence
from backend.models.validation import Validation
from backend.models.learning_pattern import LearningPattern
from backend.models.audit_log import AuditLog
from backend.database.repository import BaseRepository
from backend.schemas.incident import IncidentCreate, IncidentUpdate
from backend.core.security import get_password_hash


class TestUserModel:
    """Test User model operations."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        user = User(
            email="user1@test.com",
            hashed_password=get_password_hash("password"),
            role="VIEWER",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        assert user.id is not None
        assert user.email == "user1@test.com"
        assert user.is_active is True
        assert user.created_at is not None

    @pytest.mark.asyncio
    async def test_user_unique_email(self, db_session: AsyncSession):
        user1 = User(email="dup@test.com", hashed_password="hash1", role="VIEWER")
        db_session.add(user1)
        await db_session.commit()
        user2 = User(email="dup@test.com", hashed_password="hash2", role="VIEWER")
        db_session.add(user2)
        with pytest.raises(Exception):  # IntegrityError
            await db_session.commit()
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_soft_delete_user(self, db_session: AsyncSession):
        user = User(email="delete@test.com", hashed_password="hash", role="VIEWER")
        db_session.add(user)
        await db_session.commit()
        user.soft_delete()
        await db_session.commit()
        await db_session.refresh(user)
        assert user.is_deleted is True
        assert user.deleted_at is not None


class TestIncidentModel:
    """Test Incident model operations."""

    @pytest.mark.asyncio
    async def test_create_incident(self, db_session: AsyncSession):
        incident = Incident(
            repository="owner/repo",
            branch="main",
            pipeline_id="pipe-001",
            severity="critical",
        )
        db_session.add(incident)
        await db_session.commit()
        await db_session.refresh(incident)
        assert incident.id is not None
        assert incident.status == "OPEN"
        assert incident.retry_count == 0
        assert incident.created_at is not None

    @pytest.mark.asyncio
    async def test_incident_with_relationships(self, db_session: AsyncSession):
        incident = Incident(
            repository="owner/repo", branch="main", pipeline_id="pipe-002"
        )
        db_session.add(incident)
        await db_session.commit()
        await db_session.refresh(incident)

        action = Action(
            incident_id=incident.id,
            action_type="ADD_DEPENDENCY",
            payload={"dependency": "requests"},
        )
        db_session.add(action)
        await db_session.commit()

        evidence = Evidence(
            incident_id=incident.id,
            source="github",
            data={"error": "ModuleNotFoundError"},
        )
        db_session.add(evidence)
        await db_session.commit()

        result = await db_session.execute(
            select(Action).where(Action.incident_id == incident.id)
        )
        actions = result.scalars().all()
        assert len(actions) == 1
        assert actions[0].action_type == "ADD_DEPENDENCY"


class TestBaseRepository:
    """Test generic BaseRepository CRUD operations."""

    @pytest.mark.asyncio
    async def test_create(self, db_session: AsyncSession):
        repo = BaseRepository[Incident, IncidentCreate, IncidentUpdate](Incident)
        incident = await repo.create(
            db_session,
            obj_in=IncidentCreate(
                repository="test/repo",
                branch="main",
                pipeline_id="pipe-100",
                severity="low",
            ),
        )
        assert incident.id is not None
        assert incident.repository == "test/repo"

    @pytest.mark.asyncio
    async def test_get(self, db_session: AsyncSession):
        repo = BaseRepository[Incident, IncidentCreate, IncidentUpdate](Incident)
        created = await repo.create(
            db_session,
            obj_in=IncidentCreate(
                repository="test/get", branch="dev", pipeline_id="pipe-get"
            ),
        )
        fetched = await repo.get(db_session, created.id)
        assert fetched is not None
        assert fetched.repository == "test/get"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, db_session: AsyncSession):
        repo = BaseRepository[Incident, IncidentCreate, IncidentUpdate](Incident)
        fetched = await repo.get(db_session, uuid.uuid4())
        assert fetched is None

    @pytest.mark.asyncio
    async def test_update(self, db_session: AsyncSession):
        repo = BaseRepository[Incident, IncidentCreate, IncidentUpdate](Incident)
        created = await repo.create(
            db_session,
            obj_in=IncidentCreate(
                repository="test/update", branch="main", pipeline_id="pipe-up"
            ),
        )
        updated = await repo.update(
            db_session,
            db_obj=created,
            obj_in=IncidentUpdate(status="RESOLVED"),
        )
        assert updated.status == "RESOLVED"

    @pytest.mark.asyncio
    async def test_delete_soft(self, db_session: AsyncSession):
        repo = BaseRepository[Incident, IncidentCreate, IncidentUpdate](Incident)
        created = await repo.create(
            db_session,
            obj_in=IncidentCreate(
                repository="test/del", branch="main", pipeline_id="pipe-del"
            ),
        )
        deleted = await repo.delete(db_session, created.id)
        assert deleted is not None
        assert deleted.is_deleted is True

    @pytest.mark.asyncio
    async def test_get_all(self, db_session: AsyncSession):
        repo = BaseRepository[Incident, IncidentCreate, IncidentUpdate](Incident)
        for i in range(3):
            await repo.create(
                db_session,
                obj_in=IncidentCreate(
                    repository=f"test/all-{i}",
                    branch="main",
                    pipeline_id=f"pipe-all-{i}",
                ),
            )
        results = await repo.get_all(db_session, skip=0, limit=10)
        assert len(results) >= 3
