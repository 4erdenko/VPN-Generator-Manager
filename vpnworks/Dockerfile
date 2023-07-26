# Установка базового образа
FROM tiangolo/uvicorn-gunicorn-fastapi:latest

# Установка рабочего каталога в контейнере
WORKDIR /app

# Копирование зависимостей в контейнер
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода в контейнер
COPY . /app


