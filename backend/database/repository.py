from typing import Generic, TypeVar, Type, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid

ModelType = TypeVar("ModelType", bound=Any)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, id: uuid.UUID) -> ModelType | None:
        result = await session.execute(select(self.model).where(self.model.id == id, self.model.is_deleted == False if hasattr(self.model, "is_deleted") else True))
        return result.scalars().first()

    async def get_all(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> list[ModelType]:
        query = select(self.model)
        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)
        result = await session.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(self, session: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]) -> ModelType:
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, session: AsyncSession, id: uuid.UUID) -> ModelType | None:
        db_obj = await self.get(session, id)
        if db_obj:
            if hasattr(db_obj, "soft_delete"):
                db_obj.soft_delete()
                session.add(db_obj)
            else:
                await session.delete(db_obj)
            await session.commit()
        return db_obj
