import logging
import traceback

from aiogram import BaseMiddleware
from aiogram.types import Update

from core.config import settings

logger = logging.getLogger(__name__)


class ErrorMiddleware(BaseMiddleware):
    """
    Глобальный обработчик ошибок.
    - Логирует все необработанные исключения
    - Отправляет детали ошибки админам
    - Показывает пользователю понятное сообщение
    """

    async def __call__(self, handler, event: Update, data: dict):
        try:
            return await handler(event, data)
        except Exception as e:
            await self._handle_error(e, event, data)

    async def _handle_error(self, error: Exception, event: Update, data: dict):
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

        if event.message:
            user_id = event.message.from_user.id if event.message.from_user else None
            username = (
                event.message.from_user.username if event.message.from_user else None
            )
            context = f"message: {event.message.text or '(нет текста)'}"

            # Сообщаем пользователю
            try:
                await event.message.answer(
                    "⚠️ Произошла ошибка. Попробуйте ещё раз или обратитесь в поддержку."
                )
            except Exception:
                pass

        elif event.callback_query:
            user_id = event.callback_query.from_user.id
            username = event.callback_query.from_user.username
            context = f"callback: {event.callback_query.data}"

            try:
                await event.callback_query.answer(
                    "⚠️ Произошла ошибка. Попробуйте ещё раз.",
                    show_alert=True,
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
