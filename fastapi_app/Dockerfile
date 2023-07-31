# Установка базового образа
FROM python:3.11

# Установка рабочего каталога в контейнере
WORKDIR /fastapi_app

# Установка пути PYTHONPATH
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Копирование зависимостей в контейнер
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода в контейнер
COPY . .
