from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


class UserRepository:

    async def get_by_telegram_id(
        self,
        session: AsyncSession,
        telegram_id: int,
    ) -> User | None:
        stmt = select(User).where(
            User.telegram_id == telegram_id
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def create(
        self,
        session: AsyncSession,
        telegram_id: int,
        username: str | None,
    ) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
        )

        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user

    async def update_name(
            self,
            session,
            user_id: int,
            first_name: str,
    ):
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(first_name=first_name)
        )

        await session.commit()

        return await session.get(
            User,
            user_id,
        )

    async def update_phone(
            self,
            session,
            user_id: int,
            phone: str,
    ):
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(phone=phone)
        )

        await session.commit()

        return await session.get(
            User,
            user_id,
        )

    async def update_address(
            self,
            session,
            user_id: int,
            address: str,
    ):
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(address=address)
        )

        await session.commit()

        return await session.get(
            User,
            user_id,
        )