from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class PaymentSettings(Base):
    """
    Реквизиты оплаты — хранятся в БД,
    меняются админом прямо из бота без перезапуска.
    """
    __tablename__ = "payment_settings"

    id: Mapped[int] = mapped_column(primary_key=True)

    bank_name: Mapped[str] = mapped_column(String(100))
    recipient: Mapped[str] = mapped_column(String(100))
    card_number: Mapped[str] = mapped_column(String(20))