from langchain_nvidia_ai_endpoints import ChatNVIDIA
from backend.core.config import settings
from pydantic import BaseModel
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from typing import TypeVar, Type
import logging
import httpx
from aiolimiter import AsyncLimiter

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class NIMService:
    def __init__(self, model: str = None):
        self.api_key = settings.NVIDIA_API_KEY
        actual_model = model or settings.NIM_MODEL
        if not self.api_key:
            logger.warning("NVIDIA_API_KEY is not set. NIMService might fail.")
        
        self.llm = ChatNVIDIA(
            model=actual_model,
            nvidia_api_key=self.api_key,
            temperature=0.1,
        )
        self._limiter = None

    @property
    def limiter(self):
        if self._limiter is None:
            self._limiter = AsyncLimiter(35, 60)
        return self._limiter

    # Retry logic, timeout handling, and rate limiting (via backoff)
    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=30),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((httpx.HTTPError, ValueError))
    )
    async def generate_structured_output(self, prompt: str, schema: Type[T]) -> T:
        """
        Never trust raw model output. This function forces structured generation
        and validates it natively against the passed Pydantic schema.
        """
        async with self.limiter:
            structured_llm = self.llm.with_structured_output(schema)
            try:
                result = await structured_llm.ainvoke(prompt)
                return result
            except Exception as e:
                logger.error(f"Failed to parse structured output from NIM: {e}")
                raise ValueError(f"AI response did not match schema: {e}")

nim_service = NIMService()
