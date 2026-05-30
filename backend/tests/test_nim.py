import pytest
from unittest.mock import AsyncMock, patch
from backend.services.nim import nim_service
from pydantic import BaseModel

class DummySchema(BaseModel):
    result: str

@pytest.mark.asyncio
@patch("langchain_nvidia_ai_endpoints.ChatNVIDIA.with_structured_output")
async def test_generate_structured_output(mock_with_structured_output):
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = DummySchema(result="success")
    mock_with_structured_output.return_value = mock_llm

    result = await nim_service.generate_structured_output("test prompt", DummySchema)
    assert result.result == "success"
    mock_llm.ainvoke.assert_called_once_with("test prompt")
