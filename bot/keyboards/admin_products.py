from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


def admin_products_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Список товаров",
                    callback_data="products_list",
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Добавить товар",
                    callback_data="product_add",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="admin_back",
                )
            ]
        ]
    )


def product_manage_keyboard(
        product_id: int,
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data=f"edit_product:{product_id}"
                )
            ]
        ]
    )


def edit_product_keyboard(
        product_id: int,
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Название",
                    callback_data=f"name:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Описание",
                    callback_data=f"description:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Цена",
                    callback_data=f"price:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📦 Остаток",
                    callback_data=f"stock:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🖼 Фото",
                    callback_data=f"photo:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📂 Категория",
                    callback_data=f"change_category:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"delete_product:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ К товарам",
                    callback_data="admin_products",
                )
            ]
        ]
    )


def confirm_delete_keyboard(
        product_id: int,
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да",
                    callback_data=f"confirm_delete:{product_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Нет",
                    callback_data=f"edit_product:{product_id}",
                )
            ]
        ]
    )

def products_page_keyboard(
        page: int,
):
    buttons = []

    row = []

    if page > 0:
        row.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"products_page:{page-1}",
            )
        )

    row.append(
        InlineKeyboardButton(
            text=f"{page + 1}",
            callback_data="ignore",
        )
    )

    row.append(
        InlineKeyboardButton(
            text="➡️",
            callback_data=f"products_page:{page+1}",
        )
    )

    buttons.append(row)

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="admin_products",
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )

def products_list_keyboard(
        products,
        page: int,
):
    buttons = []

    for product in products:
        buttons.append([
            InlineKeyboardButton(
                text=product.name,
                callback_data=f"edit_product:{product.id}",
            )
        ])

    pagination = []

    if page > 0:
        pagination.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"products_page:{page-1}",
            )
        )

    pagination.append(
        InlineKeyboardButton(
            text=f"{page + 1}",
            callback_data="ignore",
        )
    )

    pagination.append(
        InlineKeyboardButton(
            text="➡️",
            callback_data=f"products_page:{page+1}",
        )
    )

    buttons.append(pagination)

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="admin_products",
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )