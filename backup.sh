#!/bin/bash
set -e

BACKUP_DIR="$HOME/backups"
DB_CONTAINER="shop_db"
DB_NAME="shop_bot"
DB_USER="postgres"
KEEP_DAYS=7

mkdir -p "$BACKUP_DIR"

DATE=$(date +"%Y-%m-%d_%H-%M")
FILENAME="$BACKUP_DIR/shop_bot_$DATE.dump"

echo "==> Создаём бэкап: $FILENAME"

docker exec "$DB_CONTAINER" pg_dump \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -F c \
    > "$FILENAME"

if [ ! -s "$FILENAME" ]; then
    echo "❌ Ошибка: файл бэкапа пустой!"
    exit 1
fi

SIZE=$(du -sh "$FILENAME" | cut -f1)
echo "✅ Бэкап создан: $FILENAME ($SIZE)"

find "$BACKUP_DIR" -name "shop_bot_*.dump" -mtime +$KEEP_DAYS -delete

echo "==> Текущие бэкапы:"
ls -lh "$BACKUP_DIR"

echo "✅ Готово"
