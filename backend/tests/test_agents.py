import pytest
from unittest.mock import patch, AsyncMock
from backend.agents.core import agent_system
from backend.agents.schemas import ClassificationResult

@pytest.mark.asyncio
@patch("backend.services.nim.NIMService.generate_structured_output", new_callable=AsyncMock)
async def test_classify_failure(mock_generate):
    mock_generate.return_value = ClassificationResult(failure_category="TEST_FAILURE")
    result = await agent_system.classify_failure("pytest failed")
    assert result.failure_category == "TEST_FAILURE"
    mock_generate.assert_called_once()
