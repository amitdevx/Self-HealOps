import logging
from sqlalchemy import select
from backend.database.session import async_session_factory
from backend.models.learning_pattern import LearningPattern

logger = logging.getLogger(__name__)

class LearningService:
    async def find_match(self, signature: str) -> LearningPattern | None:
        async with async_session_factory() as session:
            result = await session.execute(
                select(LearningPattern).where(LearningPattern.failure_signature == signature)
            )
            return result.scalar_one_or_none()

learning_service = LearningService()
