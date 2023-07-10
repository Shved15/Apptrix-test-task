#!/bin/sh
# Подождать подключения к базе данных потом выполнить миграции
while ! nc -z $DB_HOST $DB_PORT; do sleep 1; done;

python3 manage.py migrate

export PGPASSWORD=$DB_PASS

psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f /app/creation_db_data.sql