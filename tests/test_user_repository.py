import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user import UserRepository
from conftest import make_user

repo = UserRepository()


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession):
    """Создание нового пользователя."""
    user = await repo.create(
        session=session,
        telegram_id=111,
        username="ivan",
    )

    assert user.id is not None
    assert user.telegram_id == 111
    assert user.username == "ivan"


@pytest.mark.asyncio
async def test_get_by_telegram_id_found(session: AsyncSession):
    """Пользователь найден по telegram_id."""
    await make_user(session, telegram_id=222)

    user = await repo.get_by_telegram_id(
        session=session,
        telegram_id=222,
    )

    assert user is not None
    assert user.telegram_id == 222


@pytest.mark.asyncio
async def test_get_by_telegram_id_not_found(session: AsyncSession):
    """Несуществующий telegram_id возвращает None."""
    user = await repo.get_by_telegram_id(
        session=session,
        telegram_id=999999,
    )

    assert user is None


@pytest.mark.asyncio
async def test_update_fields(session: AsyncSession):
    """Обновление полей профиля пользователя."""
    user = await make_user(session, telegram_id=333)

    updated = await repo.update_fields(
        session=session,
        user_id=user.id,
        first_name="Иван",
        phone="+79991234567",
        address="Москва, ул. Тестовая, 1",
    )

    assert updated.first_name == "Иван"
    assert updated.phone == "+79991234567"
    assert updated.address == "Москва, ул. Тестовая, 1"


@pytest.mark.asyncio
async def test_update_fields_partial(session: AsyncSession):
    """Частичное обновление — остальные поля не сбрасываются."""
    user = await make_user(
        session,
        telegram_id=444,
        first_name="Пётр",
        phone="+70000000000",
    )

    await repo.update_fields(
        session=session,
        user_id=user.id,
        first_name="Иван",
    )

    updated = await repo.get_by_telegram_id(
        session=session,
        telegram_id=444,
    )

    assert updated.first_name == "Иван"
    assert updated.phone == "+70000000000"  # не изменился
