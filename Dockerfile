FROM python:3.8-alpine

# Устанавливаем рабочую директорию в контейнере
WORKDIR ./
# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Устанавливаем зависимости
RUN pip install --upgrade pip
COPY ./requirements.txt .

RUN pip install --no-cache-dir -r ./requirements.txt
# Копируем проект в рабочую директорию
COPY . .

# Сделать скрипт исполняемым
RUN chmod +x /start.sh

# Запуск скрипта при запуске контейнера
CMD ["/start.sh"]
