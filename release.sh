#!/bin/bash

python manage.py migrate admin zero
python manage.py migrate auth zero
python manage.py migrate contenttypes zero
python manage.py migrate sessions zero
python manage.py makemigrations main
python manage.py migrate main
python manage.py makemigrations
python manage.py migrate
python manage.py populate