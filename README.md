# 🛒 Telegram Shop Bot

Полнофункциональный интернет-магазин в Telegram, реализованный на **Python**, **Aiogram 3**, **SQLAlchemy**, **PostgreSQL** и **Docker**.

## 🚀 Возможности

### Для пользователей

* Просмотр каталога товаров
* Категории товаров
* Корзина покупок
* Оформление заказов
* История заказов
* Профиль пользователя
* Поддержка клиентов
* Оплата по реквизитам
* Отслеживание статуса заказа

### Для администратора

* Управление товарами
* Добавление товаров
* Редактирование товаров
* Удаление товаров
* Управление заказами
* Изменение статусов заказов
* Добавление трек-номеров отправлений
* Просмотр статистики продаж
* Просмотр платежей

---

# 🏗 Архитектура проекта

Проект построен по принципам разделения ответственности:

```text
bot/
├── handlers/
├── keyboards/
├── middlewares/
├── states/
├── repositories/
├── filters/
└── utils/

core/
├── config.py
├── database.py
└── database_init.py

models/
├── user.py
├── product.py
├── category.py
├── cart_item.py
├── order.py
└── order_item.py

services/
└──user.py

tests/
├── conftest.py
├── test_cart_repository.py
├── test_category_repository.py
├── test_order_repository.py
├── test_product_repository.py
├── test_user_repository.py
└── test_user_service.py
```

### Используемые паттерны

* Repository Pattern
* Service Layer
* Dependency Injection
* FSM (Finite State Machine)
* Middleware

---

# 🛠 Технологии

* Python 3.12
* Aiogram 3
* SQLAlchemy 2.0
* PostgreSQL
* AsyncPG
* Alembic
* Docker
* Docker Compose
* Pytest
* Pytest-Asyncio

---

# 📦 Установка

## Клонирование репозитория

```bash
git clone https://github.com/USERNAME/shop_bot.git

cd shop_bot
```

## Создание .env

```env
BOT_TOKEN=your_bot_token

DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=

POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

# Реквизиты для оплаты
PAYMENT_BANK_NAME=
PAYMENT_RECIPIENT=
PAYMENT_CARD_NUMBER=

# ID администраторов через запятую
ADMIN_IDS=
```

---

# 🐳 Запуск через Docker

Сборка контейнеров:

```bash
docker compose build
```

Запуск:

```bash
docker compose up -d
```

Проверка логов:

```bash
docker compose logs -f
```

Остановка:

```bash
docker compose down
```

---

# 🗄 Работа с базой данных

Подключение к PostgreSQL внутри контейнера:

```bash
docker compose exec db psql -U postgres -d shop_bot
```

Просмотр таблиц:

```sql
\dt
```

---

# 📥 Перенос данных

Создание дампа:

```bash
pg_dump -U postgres -d shop_bot > shop_bot.sql
```

Восстановление в Docker:

```bash
cat shop_bot.sql | docker compose exec -T db psql -U postgres -d shop_bot
```

---

# 🧪 Тестирование

Запуск всех тестов:

```bash
pytest -v
```

Запуск с покрытием:

```bash
python -m pytest --cov=repositories --cov=services --cov-report=html
```

Отчёт будет доступен в папке:

```text
htmlcov/
```

---

# 📊 Покрытие тестами

Покрыты тестами:

* UserRepository
* ProductRepository
* CartRepository
* CategoryRepository
* OrderRepository
* UserService

Текущее покрытие проекта:

```text
36 tests passed
```

---

# 📋 Основные сущности

### User

Пользователь Telegram.

### Category

Категория товаров.

### Product

Товар магазина.

### CartItem

Товар в корзине пользователя.

### Order

Заказ пользователя.

### OrderItem

Позиция внутри заказа.

---

# 🔒 Возможные улучшения

* Интеграция платежных систем
* Redis для FSM
* Celery для фоновых задач
* Админ-панель через Web UI
* Логи и мониторинг
* CI/CD через GitHub Actions
* Автоматический деплой на Yandex Cloud

---

# 👨‍💻 Автор

Максим Меркулов

Python Backend Developer

Стек:

* Python
* FastAPI
* Django
* SQLAlchemy
* PostgreSQL
* Docker
* Aiogram
* Git
* Linux
