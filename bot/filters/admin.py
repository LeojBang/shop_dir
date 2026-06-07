from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from core.config import settings


class AdminFilter(BaseFilter):

    async def __call__(
        self,
        event: Message | CallbackQuery,
    ) -> bool:
        return event.from_user.id in settings.ADMIN_IDS
