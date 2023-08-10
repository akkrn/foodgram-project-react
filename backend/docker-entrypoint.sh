#!/bin/sh
python manage.py collectstatic
cp -r --force /app/collected_static/. /backend_static/static/
python manage.py migrate
gunicorn --bind 0.0.0.0:8888 foodgram.wsgi
