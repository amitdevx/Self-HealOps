import pytest
from backend.models.user import User
from backend.models.incident import Incident

@pytest.mark.asyncio
async def test_user_creation():
    user = User(email="test@example.com", hashed_password="hashed")
    assert user.email == "test@example.com"

@pytest.mark.asyncio
async def test_incident_creation():
    incident = Incident(repository="repo-test", branch="main", pipeline_id="123")
    assert incident.repository == "repo-test"
