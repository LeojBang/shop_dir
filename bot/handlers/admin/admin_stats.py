from collections import defaultdict
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.admin import AdminFilter
from repositories.order import OrderRepository
from repositories.product import ProductRepository
from repositories.user import UserRepository

router = Router()
router.callback_query.filter(AdminFilter())

order_repository = OrderRepository()
product_repository = ProductRepository()
user_repository = UserRepository()


def build_bar(value: float, max_value: float, width: int = 10) -> str:
    """Рисует текстовый прогресс-бар."""
    if max_value == 0:
        filled = 0
    else:
        filled = round((value / max_value) * width)
    return "█" * filled + "░" * (width - filled)


def build_stats_text(
    all_orders,
    total_users: int,
    low_stock_products,
) -> str:
    now = datetime.utcnow()
    today = now.date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # ── Фильтруем по статусам ────────────────────────────────────────────────
    completed = [o for o in all_orders if o.status == "completed"]
    cancelled = [o for o in all_orders if o.status == "cancelled"]
    waiting = [o for o in all_orders if o.status == "waiting_payment"]
    processing = [o for o in all_orders if o.status == "processing"]
    payment_check = [o for o in all_orders if o.status == "payment_check"]

    active = waiting + processing + payment_check

    # ── Выручка ──────────────────────────────────────────────────────────────
    revenue_total = sum(float(o.total_price) for o in completed)
    revenue_month = sum(
        float(o.total_price) for o in completed if o.created_at.date() >= month_ago
    )
    revenue_week = sum(
        float(o.total_price) for o in completed if o.created_at.date() >= week_ago
    )
    revenue_today = sum(
        float(o.total_price) for o in completed if o.created_at.date() == today
    )

    # ── Заказы по дням (последние 7 дней) ────────────────────────────────────
    orders_by_day: dict = defaultdict(int)
    revenue_by_day: dict = defaultdict(float)

    for o in completed:
        if o.created_at.date() >= week_ago:
            day = o.created_at.strftime("%d.%m")
            orders_by_day[day] += 1
            revenue_by_day[day] += float(o.total_price)

    max_orders_day = max(orders_by_day.values(), default=1)

    # ── Топ товаров ───────────────────────────────────────────────────────────
    product_sales: dict = defaultdict(int)
    for o in completed:
        for item in o.items:
            product_sales[item.product.name] += item.quantity

    top_products = sorted(
        product_sales.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:5]

    max_sales = top_products[0][1] if top_products else 1

    # ── Средний чек ───────────────────────────────────────────────────────────
    avg_check = revenue_total / len(completed) if completed else 0

    # ── Конверсия ─────────────────────────────────────────────────────────────
    conversion = len(completed) / len(all_orders) * 100 if all_orders else 0

    # ── Строим текст ──────────────────────────────────────────────────────────
    lines = [
        "📊 <b>Статистика магазина</b>",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "💰 <b>Выручка</b>",
        f"  Сегодня:    <b>{revenue_today:,.0f} ₽</b>",
        f"  Неделя:     <b>{revenue_week:,.0f} ₽</b>",
        f"  Месяц:      <b>{revenue_month:,.0f} ₽</b>",
        f"  Всего:      <b>{revenue_total:,.0f} ₽</b>",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "📦 <b>Заказы</b>",
        f"  Всего:      {len(all_orders)}",
        f"  ✅ Выполнено: {len(completed)}",
        f"  ⏳ Активных:  {len(active)}",
        f"  ❌ Отменено:  {len(cancelled)}",
        f"  📈 Конверсия: {conversion:.1f}%",
        f"  💳 Ср. чек:   {avg_check:,.0f} ₽",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "👥 <b>Пользователи</b>",
        f"  Всего: {total_users}",
    ]

    # ── График по дням ────────────────────────────────────────────────────────
    if orders_by_day:
        lines += [
            "",
            "━━━━━━━━━━━━━━━━━━━━",
            "📅 <b>Последние 7 дней</b>",
        ]
        for i in range(7):
            day = (today - timedelta(days=6 - i)).strftime("%d.%m")
            count = orders_by_day.get(day, 0)
            rev = revenue_by_day.get(day, 0)
            bar = build_bar(count, max_orders_day, width=8)
            lines.append(f"  {day} {bar} {count} зак. / {rev:,.0f} ₽")

    # ── Топ товаров ───────────────────────────────────────────────────────────
    if top_products:
        lines += [
            "",
            "━━━━━━━━━━━━━━━━━━━━",
            "🏆 <b>Топ товаров</b>",
        ]
        for i, (name, qty) in enumerate(top_products, 1):
            bar = build_bar(qty, max_sales, width=6)
            # Обрезаем длинные названия
            short_name = name[:20] + "…" if len(name) > 20 else name
            lines.append(f"  {i}. {short_name}")
            lines.append(f"     {bar} {qty} шт.")

    # ── Заканчивающиеся товары ────────────────────────────────────────────────
    if low_stock_products:
        lines += [
            "",
            "━━━━━━━━━━━━━━━━━━━━",
            "⚠️ <b>Заканчиваются</b>",
        ]
        for p in low_stock_products:
            lines.append(f"  • {p.name}: {p.stock} шт.")

    lines += [
        "",
        f"🕐 Обновлено: {now.strftime('%d.%m.%Y %H:%M')}",
    ]

    return "\n".join(lines)


@router.callback_query(F.data == "admin_stats")
async def admin_stats(
    callback: CallbackQuery,
    session: AsyncSession,
):
    all_orders = await order_repository.get_all_orders(session=session)

    # Считаем пользователей
    from sqlalchemy import func, select

    from models.user import User

    total_users = await session.scalar(select(func.count()).select_from(User)) or 0

    # Товары с остатком <= 3
    from sqlalchemy import select as sa_select

    from models.product import Product

    result = await session.execute(
        sa_select(Product)
        .where(Product.stock <= 3)
        .where(Product.stock > 0)
        .order_by(Product.stock)
    )
    low_stock = list(result.scalars().all())

    text = build_stats_text(all_orders, total_users, low_stock)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
    )
    await callback.answer()
