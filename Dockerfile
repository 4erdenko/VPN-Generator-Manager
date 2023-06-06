FROM python:3.8-alpine

WORKDIR ./

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r ./requirements.txt
# Копируем проект в рабочую директорию
COPY . .

# Сделать скрипт исполняемым
RUN chmod +x /start.sh

# Запуск скрипта при запуске контейнера
CMD ["/start.sh"]
