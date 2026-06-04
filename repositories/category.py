from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.category import Category


class CategoryRepository:

    async def get_all(
        self,
        session: AsyncSession,
    ) -> list[Category]:
        result = await session.execute(
            select(Category)
        )

        return list(result.scalars().all())