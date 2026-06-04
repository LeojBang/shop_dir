from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware

from core.database import async_session


class DatabaseMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable,
        event: Any,
        data: Dict[str, Any],
    ):
        async with async_session() as session:
            data["session"] = session

            return await handler(event, data)