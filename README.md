# 🛒 ShopPeptid Bot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Aiogram](https://img.shields.io/badge/Aiogram-3.x-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

Полнофункциональный магазин в Telegram с каталогом товаров, корзиной, оплатой и админ-панелью.

</div>

---

## ✨ Возможности

### 👤 Для покупателей
| Функция | Описание |
|---|---|
| 📦 Каталог | Товары по категориям с остатками на складе |
| 🛒 Корзина | Добавление, изменение количества, удаление |
| 🧾 Оформление | Минимальная сумма заказа, бесплатная доставка |
| 💳 Оплата | Перевод на карту с подтверждением |
| 📋 История | Список заказов с деталями и трек-номером |
| 👤 Профиль | Имя, телефон, адрес ПВЗ Ozon |
| ☎️ Поддержка | Контакты менеджера |

### ⚙️ Для администратора
| Функция | Описание |
|---|---|
| 📦 Товары | Добавление, редактирование, удаление |
| 🧾 Заказы | Просмотр, смена статуса, трек-номер |
| 💳 Оплата | Подтверждение и отклонение оплаты |
| 💰 Реквизиты | Смена банка/карты прямо из бота |
| 📊 Статистика | Выручка, топ товаров, график по дням |

---

## 🏗 Архитектура

```
shop_dir/
├── bot/
│   ├── handlers/          # Обработчики сообщений и callback
│   │   └── admin/         # Админские хендлеры
│   ├── keyboards/         # Inline и Reply клавиатуры
│   ├── middlewares/       # Database, Antispam, Error
│   ├── states/            # FSM состояния
│   ├── filters/           # AdminFilter
│   └── utils/             # Вспомогательные утилиты
├── core/
│   ├── config.py          # Настройки через pydantic-settings
│   ├── database.py        # Подключение к БД
│   ├── database_init.py   # Инициализация таблиц
│   └── logger.py          # Настройка логирования
├── models/                # SQLAlchemy модели
├── repositories/          # Слой работы с БД
├── services/              # Бизнес-логика
├── migrations/            # Alembic миграции
├── tests/                 # Pytest тесты
├── logs/                  # Логи (gitignore)
├── Dockerfile
└── docker-compose.yaml
```

### Паттерны
- **Repository Pattern** — изоляция работы с БД
- **Service Layer** — бизнес-логика отдельно от хендлеров
- **Middleware** — обработка ошибок, антиспам, сессии БД
- **FSM** — управление состояниями диалогов

---

## 🛠 Стек технологий

- **Python 3.12** + **Aiogram 3** — бот
- **SQLAlchemy 2.0** + **AsyncPG** — асинхронная работа с БД
- **PostgreSQL 17** — база данных
- **Alembic** — миграции
- **Docker** + **Docker Compose** — контейнеризация
- **GitHub Actions** — CI/CD
- **Pytest** + **pytest-asyncio** — тесты на SQLite in-memory
- **Black** + **Flake8** — форматирование и линтинг

---

## 🚀 Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/USERNAME/shop_dir.git
cd shop_dir
```

### 2. Создать `.env`

```env
BOT_TOKEN=your_bot_token

DB_HOST=db
DB_PORT=5432
DB_NAME=shop_bot
DB_USER=postgres
DB_PASSWORD=your_password

POSTGRES_DB=shop_bot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Реквизиты оплаты
PAYMENT_BANK_NAME=OZON BANK
PAYMENT_RECIPIENT=Иванов Иван
PAYMENT_CARD_NUMBER=2200000000000000

# ID администраторов (через запятую)
ADMIN_IDS=[123456789]
```

### 3. Запустить

```bash
docker compose up -d --build
docker compose exec bot alembic upgrade head
```

### 4. Проверить

```bash
docker compose ps
docker compose logs bot -f
```

---

## 🧪 Тесты

```bash
# Все тесты
python -m pytest tests/ -v

# С покрытием
python -m pytest tests/ -v --cov=repositories --cov=services --cov-report=term-missing
```

**Покрыто тестами:** `UserRepository`, `ProductRepository`, `CartRepository`, `OrderRepository`, `UserService`, `PaymentSettingsRepository` — 52 тестов.

---

## 🗄 База данных

```bash
# Зайти в psql
docker compose exec db psql -U postgres -d shop_bot

# Применить миграции
docker compose exec bot alembic upgrade head

# Создать новую миграцию
docker compose exec bot alembic revision --autogenerate -m "description"
```

## 📊 CI/CD

При пуше в `main`:
1. Запускаются тесты + Black + Flake8
2. При успехе — деплой на сервер по SSH
3. `git pull` → `docker compose build` → `alembic upgrade head`

Для настройки добавить в GitHub Secrets: `SERVER_HOST`, `SERVER_USER`, `SERVER_SSH_KEY`.

---

## 📋 Статусы заказов

```
waiting_payment → payment_check → processing → completed
                                             ↘ cancelled
```

| Статус | Описание |
|---|---|
| `waiting_payment` | Ожидает оплату |
| `payment_check` | Пользователь нажал «Я оплатил» |
| `processing` | Оплата подтверждена, готовится к отправке |
| `completed` | Отправлен, трек-номер добавлен |
| `cancelled` | Отменён, товары возвращены на склад |

---

## 👨‍💻 Автор

**Максим Меркулов** — Python Backend Developer

`Python` · `Aiogram` · `FastAPI` · `Django` · `SQLAlchemy` · `PostgreSQL` · `Docker`