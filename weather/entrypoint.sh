#!/bin/bash

set -e

echo "${0}: running migrations."
python manage.py makemigrations --merge
python manage.py migrate --noinput


echo "${0}: starting server."
python manage.py runserver 0.0.0.0:8000
