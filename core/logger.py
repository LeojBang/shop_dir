import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def setup_logger() -> logging.Logger:
    """
    Настраивает логирование:
    - INFO и выше → консоль
    - WARNING и выше → файл logs/bot.log (ротация 5 МБ, 3 файла)
    - ERROR и выше → файл logs/errors.log (ротация 5 МБ, 5 файлов)
    """
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt=date_fmt)

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Консоль — всё INFO и выше
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    # Файл bot.log — WARNING и выше, ротация по 5 МБ, хранить 3 файла
    bot_file = RotatingFileHandler(
        LOG_DIR / "bot.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    bot_file.setLevel(logging.WARNING)
    bot_file.setFormatter(formatter)

    # Файл errors.log — только ERROR и выше, хранить 5 файлов
    error_file = RotatingFileHandler(
        LOG_DIR / "errors.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_file.setLevel(logging.ERROR)
    error_file.setFormatter(formatter)

    root.addHandler(console)
    root.addHandler(bot_file)
    root.addHandler(error_file)

    # Убираем лишний шум от сторонних библиотек
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

    return root


logger = setup_logger()
