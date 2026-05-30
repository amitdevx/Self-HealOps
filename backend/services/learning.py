import logging
from sqlalchemy import select
from backend.database.session import async_session_factory
from backend.models.learning_pattern import LearningPattern

logger = logging.getLogger(__name__)

class LearningService:
    async def find_match(self, signature: str) -> LearningPattern | None:
        """
        Queries the learning_patterns table for a high-confidence match 
        to bypass the NIM LLM inference loops.
        """
        async with async_session_factory() as session:
            # Semantic/exact string matching logic
            stmt = select(LearningPattern).where(LearningPattern.failure_signature == signature)
            result = await session.execute(stmt)
            match = result.scalars().first()
            if match:
                logger.info(f"Learning deduplication match found for signature: {signature}")
            else:
                logger.info("No learning pattern match found. Proceeding with LLM inference.")
            return match

learning_service = LearningService()
