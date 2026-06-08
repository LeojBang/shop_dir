import pytest
from conftest import make_user
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user import UserRepository

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
async def test_get_or_create_creates_new_user(session: AsyncSession):
    """get_or_create создаёт пользователя, если его нет."""
    user = await repo.get_or_create(
        session=session,
        telegram_id=555,
        username="newbie",
    )

    assert user.id is not None
    assert user.telegram_id == 555
    assert user.username == "newbie"


@pytest.mark.asyncio
async def test_get_or_create_returns_existing_user(session: AsyncSession):
    """get_or_create возвращает существующего пользователя, не создаёт дубль."""
    existing = await make_user(session, telegram_id=666, username="already_here")

    user = await repo.get_or_create(
        session=session,
        telegram_id=666,
        username="already_here",
    )

    assert user.id == existing.id


@pytest.mark.asyncio
async def test_get_or_create_no_duplicate_on_conflict(session: AsyncSession):
    """При конфликте не создаётся второй пользователь с тем же telegram_id."""
    await repo.get_or_create(session=session, telegram_id=777, username="once")
    await repo.get_or_create(session=session, telegram_id=777, username="once")

    # Убеждаемся что в БД ровно одна запись
    from sqlalchemy import func, select

    from models.user import User

    result = await session.execute(select(func.count()).where(User.telegram_id == 777))
    count = result.scalar()
    assert count == 1


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
