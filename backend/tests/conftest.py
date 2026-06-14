import pytest
import asyncio
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

from backend.database.base import Base
from backend.models.user import User
from backend.models.incident import Incident
from backend.core.security import get_password_hash, create_access_token



@pytest.fixture
async def async_engine():
    """Create a fresh async test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(async_engine):
    """Create a test database session."""
    session_factory = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test admin user."""
    user = User(
        id=uuid.uuid4(),
        email="admin@test.com",
        hashed_password=get_password_hash("testpassword"),
        role="ADMIN",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """Create a JWT auth token for the test user."""
    return create_access_token(subject=str(test_user.id))


@pytest.fixture
def auth_headers(auth_token):
    """Create auth headers for API requests."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def test_incident(db_session: AsyncSession):
    """Create a test incident."""
    incident = Incident(
        id=uuid.uuid4(),
        repository="test/repo",
        branch="main",
        pipeline_id="pipeline-123",
        severity="high",
        status="OPEN",
    )
    db_session.add(incident)
    await db_session.commit()
    await db_session.refresh(incident)
    return incident


@pytest.fixture
async def app_with_test_db(async_engine):
    """Create a FastAPI test app with test database."""
    session_factory = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async def override_get_db():
        async with session_factory() as session:
            yield session

    # Patch the Celery task to prevent actual task dispatch
    with patch("backend.workers.worker.process_incident") as mock_task:
        mock_task.delay = MagicMock()
        from backend.main import create_app
        from backend.core.dependencies import get_db
        app = create_app()
        app.dependency_overrides[get_db] = override_get_db
        yield app, session_factory
        app.dependency_overrides.clear()


from fastapi.testclient import TestClient

@pytest.fixture
def client(app_with_test_db):
    """Create a sync HTTP test client."""
    app, _ = app_with_test_db
    with TestClient(app) as c:
        yield c
