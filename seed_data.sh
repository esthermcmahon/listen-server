#!/bin/bash

rm -rf listenapi/migrations
rm db.sqlite3
python manage.py makemigrations listenapi
python manage.py migrate
python manage.py loaddata users
python manage.py loaddata tokens
python manage.py loaddata musicians
python manage.py loaddata categories
python manage.py loaddata excerpts
python manage.py loaddata recordings
python manage.py loaddata comments
python manage.py loaddata connections
python manage.py loaddata goals

