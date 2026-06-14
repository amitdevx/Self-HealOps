import pytest
import tenacity
from unittest.mock import patch, AsyncMock, MagicMock
from pydantic import BaseModel
from backend.services.nim import NIMService


class DummySchema(BaseModel):
    result: str
    score: float = 0.0


class TestNIMService:
    """Test NIM service with mocked LLM calls."""

    @pytest.fixture
    def nim(self):
        with patch("backend.services.nim.ChatNVIDIA") as mock_chat:
            service = NIMService(model="test-model")
            yield service, mock_chat

    @pytest.mark.asyncio
    async def test_generate_structured_output_success(self, nim):
        service, _ = nim
        expected = DummySchema(result="success", score=0.95)
        mock_structured = AsyncMock()
        mock_structured.ainvoke.return_value = expected
        service.llm.with_structured_output = MagicMock(return_value=mock_structured)

        result = await service.generate_structured_output("test prompt", DummySchema)
        assert result.result == "success"
        assert result.score == 0.95

    @pytest.mark.asyncio
    async def test_generate_structured_output_raises_on_failure(self, nim):
        service, _ = nim
        mock_structured = AsyncMock()
        mock_structured.ainvoke.side_effect = Exception("Parse error")
        service.llm.with_structured_output = MagicMock(return_value=mock_structured)

        with pytest.raises(tenacity.RetryError):
            await service.generate_structured_output("bad prompt", DummySchema)
