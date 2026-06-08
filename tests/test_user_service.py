import asyncio

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from services.user import UserService

service = UserService()


@pytest.mark.asyncio
async def test_register_new_user(session: AsyncSession):
    """Новый пользователь создаётся при первом /start."""
    user = await service.register_user(
        session=session,
        telegram_id=201,
        username="newuser",
    )

    assert user.id is not None
    assert user.telegram_id == 201
    assert user.username == "newuser"


@pytest.mark.asyncio
async def test_register_user_concurrent_no_duplicate(session_factory):
    """Два одновременных /start не создают дубль пользователя."""
    async with session_factory() as s1, session_factory() as s2:
        results = await asyncio.gather(
            service.register_user(session=s1, telegram_id=204, username="race"),
            service.register_user(session=s2, telegram_id=204, username="race"),
            return_exceptions=True,
        )

    for r in results:
        assert not isinstance(r, Exception)

    ids = {r.id for r in results if not isinstance(r, Exception)}
    assert len(ids) == 1


@pytest.mark.asyncio
async def test_register_existing_user_returns_same(session: AsyncSession):
    """Повторный /start возвращает того же пользователя, не создаёт нового."""
    first = await service.register_user(
        session=session,
        telegram_id=202,
        username="existing",
    )

    second = await service.register_user(
        session=session,
        telegram_id=202,
        username="existing",
    )

    assert first.id == second.id


@pytest.mark.asyncio
async def test_register_user_without_username(session: AsyncSession):
    """Пользователь без username (приватный аккаунт) создаётся корректно."""
    user = await service.register_user(
        session=session,
        telegram_id=203,
        username=None,
    )

    assert user.id is not None
    assert user.username is None
