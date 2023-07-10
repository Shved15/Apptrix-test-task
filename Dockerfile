FROM python:3.11

WORKDIR /app

# Обновляем систему и устанавливаем необходимые системные библиотеки
RUN apt-get update && apt-get install -y binutils libproj-dev gdal-bin netcat-openbsd postgresql-client redis-server

# Копируем код приложения в контейнер
COPY . /app

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

CMD ["./cmds.sh"]
