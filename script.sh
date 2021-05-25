#!/bin/bash

python3 /code/backend/load_data.py
cd /code/backend/movies_admin/
python3 manage.py migrate movies --fake-initial
python3 manage.py migrate
python3 manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8010
#python3 /code/backend/movies_admin/manage.py runserver 0.0.0.0:8010

