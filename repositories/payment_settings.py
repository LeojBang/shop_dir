from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.payment_settings import PaymentSettings
from core.config import settings as env_settings


class PaymentSettingsRepository:

    async def get(self, session: AsyncSession) -> PaymentSettings | None:
        """Возвращает текущие реквизиты из БД."""
        result = await session.execute(
            select(PaymentSettings).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_or_default(self, session: AsyncSession) -> PaymentSettings:
        """
        Возвращает реквизиты из БД.
        Если ещё не заданы — создаёт запись из .env (первый запуск).
        """
        record = await self.get(session)

        if record is None:
            record = PaymentSettings(
                bank_name=env_settings.PAYMENT_BANK_NAME,
                recipient=env_settings.PAYMENT_RECIPIENT,
                card_number=env_settings.PAYMENT_CARD_NUMBER,
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)

        return record

    async def update(
        self,
        session: AsyncSession,
        bank_name: str | None = None,
        recipient: str | None = None,
        card_number: str | None = None,
    ) -> PaymentSettings:
        """Обновляет только переданные поля."""
        record = await self.get_or_default(session)

        if bank_name is not None:
            record.bank_name = bank_name
        if recipient is not None:
            record.recipient = recipient
        if card_number is not None:
            record.card_number = card_number

        await session.commit()
        await session.refresh(record)
        return record