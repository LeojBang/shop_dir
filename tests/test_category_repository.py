import pytest

from repositories.category import CategoryRepository
from tests.conftest import make_category

repo = CategoryRepository()


@pytest.mark.asyncio
async def test_get_all_categories(session):
    await make_category(
        session,
        name="Пептиды",
    )

    await make_category(
        session,
        name="Витамины",
    )

    categories = await repo.get_all(session)

    assert len(categories) == 2

    names = [c.name for c in categories]

    assert "Пептиды" in names
    assert "Витамины" in names


@pytest.mark.asyncio
async def test_get_all_categories_empty(session):
    categories = await repo.get_all(session)

    assert categories == []
