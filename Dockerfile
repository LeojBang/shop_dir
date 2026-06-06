FROM python:3.12-slim

# Логи сразу выводятся в консоль без буферизации
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Сначала копируем только requirements — слой кешируется
# и не пересобирается при изменении кода
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

CMD ["python", "main.py"]