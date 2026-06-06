import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from repositories.payment_settings import PaymentSettingsRepository
from models.payment_settings import PaymentSettings
import repositories.payment_settings as repo_module

repo = PaymentSettingsRepository()

BANK = "TEST BANK"
RECIPIENT = "Тестов Тест"
CARD = "1234567890123456"


async def seed(session: AsyncSession) -> PaymentSettings:
    """Создаёт запись реквизитов напрямую без .env."""
    record = PaymentSettings(
        bank_name=BANK,
        recipient=RECIPIENT,
        card_number=CARD,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


# ── get ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_returns_none_when_empty(session: AsyncSession):
    """get() возвращает None если таблица пустая."""
    result = await repo.get(session)
    assert result is None


@pytest.mark.asyncio
async def test_get_returns_record_when_exists(session: AsyncSession):
    """get() возвращает запись если она есть."""
    await seed(session)
    result = await repo.get(session)
    assert result is not None
    assert result.bank_name == BANK


# ── get_or_default ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_or_default_creates_from_env_when_empty(session: AsyncSession, monkeypatch):
    """get_or_default() создаёт запись из .env если таблица пустая."""
    monkeypatch.setattr(repo_module.env_settings, "PAYMENT_BANK_NAME", BANK)
    monkeypatch.setattr(repo_module.env_settings, "PAYMENT_RECIPIENT", RECIPIENT)
    monkeypatch.setattr(repo_module.env_settings, "PAYMENT_CARD_NUMBER", CARD)

    result = await repo.get_or_default(session)

    assert result.id is not None
    assert result.bank_name == BANK
    assert result.recipient == RECIPIENT
    assert result.card_number == CARD


@pytest.mark.asyncio
async def test_get_or_default_returns_existing_record(session: AsyncSession, monkeypatch):
    """get_or_default() возвращает существующую запись без создания новой."""
    await seed(session)

    monkeypatch.setattr(repo_module.env_settings, "PAYMENT_BANK_NAME", "OTHER BANK")
    monkeypatch.setattr(repo_module.env_settings, "PAYMENT_RECIPIENT", "Другой Человек")
    monkeypatch.setattr(repo_module.env_settings, "PAYMENT_CARD_NUMBER", "0000000000000000")

    result = await repo.get_or_default(session)

    # Должна вернуться запись из БД, а не из .env
    assert result.bank_name == BANK
    assert result.recipient == RECIPIENT


@pytest.mark.asyncio
async def test_get_or_default_does_not_create_duplicate(session: AsyncSession, monkeypatch):
    """get_or_default() не создаёт вторую запись при повторном вызове."""
    monkeypatch.setattr(repo_module.env_settings, "PAYMENT_BANK_NAME", BANK)
    monkeypatch.setattr(repo_module.env_settings, "PAYMENT_RECIPIENT", RECIPIENT)
    monkeypatch.setattr(repo_module.env_settings, "PAYMENT_CARD_NUMBER", CARD)

    first = await repo.get_or_default(session)
    second = await repo.get_or_default(session)

    assert first.id == second.id

    count = await session.scalar(
        select(func.count()).select_from(PaymentSettings)
    )
    assert count == 1


# ── update ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_bank_name(session: AsyncSession):
    """update() меняет только bank_name."""
    await seed(session)
    result = await repo.update(session, bank_name="НОВЫЙ БАНК")

    assert result.bank_name == "НОВЫЙ БАНК"
    assert result.recipient == RECIPIENT   # не изменился
    assert result.card_number == CARD      # не изменился


@pytest.mark.asyncio
async def test_update_recipient(session: AsyncSession):
    """update() меняет только recipient."""
    await seed(session)
    result = await repo.update(session, recipient="Сидоров Сидор")

    assert result.recipient == "Сидоров Сидор"
    assert result.bank_name == BANK        # не изменился


@pytest.mark.asyncio
async def test_update_card_number(session: AsyncSession):
    """update() меняет только card_number."""
    await seed(session)
    result = await repo.update(session, card_number="5555666677778888")

    assert result.card_number == "5555666677778888"
    assert result.bank_name == BANK        # не изменился


@pytest.mark.asyncio
async def test_update_all_fields(session: AsyncSession):
    """update() меняет все поля сразу."""
    await seed(session)
    result = await repo.update(
        session,
        bank_name="ТИНЬКОФФ",
        recipient="Козлов Козёл",
        card_number="4444333322221111",
    )

    assert result.bank_name == "ТИНЬКОФФ"
    assert result.recipient == "Козлов Козёл"
    assert result.card_number == "4444333322221111"


@pytest.mark.asyncio
async def test_update_persists_to_db(session: AsyncSession):
    """Обновлённые данные реально сохраняются в БД."""
    await seed(session)
    await repo.update(session, bank_name="СОХРАНЁННЫЙ БАНК")

    fresh = await repo.get(session)
    assert fresh.bank_name == "СОХРАНЁННЫЙ БАНК"


@pytest.mark.asyncio
async def test_update_none_values_do_not_change_fields(session: AsyncSession):
    """Передача None в update() не сбрасывает поля."""
    await seed(session)
    result = await repo.update(
        session,
        bank_name=None,
        recipient=None,
        card_number=None,
    )

    assert result.bank_name == BANK
    assert result.recipient == RECIPIENT
    assert result.card_number == CARD


@pytest.mark.asyncio
async def test_update_creates_record_if_not_exists(session: AsyncSession, monkeypatch):
    """update() создаёт запись если её нет — через get_or_default внутри."""
    monkeypatch.setattr(repo_module.env_settings, "PAYMENT_BANK_NAME", BANK)
    monkeypatch.setattr(repo_module.env_settings, "PAYMENT_RECIPIENT", RECIPIENT)
    monkeypatch.setattr(repo_module.env_settings, "PAYMENT_CARD_NUMBER", CARD)

    result = await repo.update(session, bank_name="АВТОСОЗДАНИЕ")

    assert result.id is not None
    assert result.bank_name == "АВТОСОЗДАНИЕ"