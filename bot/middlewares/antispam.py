import logging
import time
from collections import defaultdict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

logger = logging.getLogger(__name__)


class AntispamMiddleware(BaseMiddleware):

    def __init__(self, limit: int = 5, window: float = 3.0):
        self.limit = limit
        self.window = window
        self._user_requests: dict[int, list[float]] = defaultdict(list)

    def _is_spam(self, user_id: int) -> bool:
        now = time.monotonic()
        self._user_requests[user_id] = [
            t for t in self._user_requests[user_id] if now - t < self.window
        ]
        if len(self._user_requests[user_id]) >= self.limit:
            return True
        self._user_requests[user_id].append(now)
        return False

    async def __call__(self, handler, event: TelegramObject, data: dict):
        user_id = None

        update = data.get("event_update")
        if isinstance(update, Update):
            if update.message and update.message.from_user:
                user_id = update.message.from_user.id
            elif update.callback_query and update.callback_query.from_user:
                user_id = update.callback_query.from_user.id

        if user_id and self._is_spam(user_id):
            logger.warning("Антиспам: заблокирован user_id=%s", user_id)
            return

        return await handler(event, data)
