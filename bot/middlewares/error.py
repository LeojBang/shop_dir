import logging
import traceback

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.config import settings

logger = logging.getLogger(__name__)


class ErrorMiddleware(BaseMiddleware):
    """
    Глобальный обработчик ошибок.
    - Логирует все необработанные исключения
    - Отправляет детали ошибки админам
    - Показывает пользователю понятное сообщение
    """

    async def __call__(self, handler, event: TelegramObject, data: dict):
        try:
            return await handler(event, data)
        except Exception as e:
            await self._handle_error(e, event, data)

    async def _handle_error(self, error: Exception, event: TelegramObject, data: dict):
        tb = traceback.format_exc()

        # Логируем с полным traceback
        logger.error(
            "Необработанное исключение: %s\n%s",
            error,
            tb,
        )

        bot = data.get("bot")
        if not bot:
            return

        # Определяем откуда пришёл запрос
        user_id = None
        username = None
        context = "неизвестно"

        from aiogram.types import Update

        update = data.get("event_update")
        if isinstance(update, Update):
            if update.message and update.message.from_user:
                user_id = update.message.from_user.id
                username = update.message.from_user.username
                context = f"message: {update.message.text or '(нет текста)'}"
                try:
                    await update.message.answer(
                        "⚠️ Произошла ошибка. Попробуйте ещё раз."
                    )
                except Exception:
                    pass
            elif update.callback_query and update.callback_query.from_user:
                user_id = update.callback_query.from_user.id
                username = update.callback_query.from_user.username
                context = f"callback: {update.callback_query.data}"
                try:
                    await update.callback_query.answer(
                        "⚠️ Произошла ошибка.", show_alert=True
                    )
                except Exception:
                    pass

        # Отправляем детали ошибки всем админам
        error_text = (
            f"🔴 <b>Ошибка в боте</b>\n\n"
            f"<b>Тип:</b> {type(error).__name__}\n"
            f"<b>Сообщение:</b> {str(error)[:200]}\n\n"
            f"<b>Контекст:</b> {context}\n"
            f"<b>Пользователь:</b> {user_id} (@{username})\n\n"
            f"<b>Traceback:</b>\n"
            f"<pre>{tb[-1000:]}</pre>"
        )

        for admin_id in settings.ADMIN_IDS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=error_text,
                    parse_mode="HTML",
                )
            except Exception:
                pass
