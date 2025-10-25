#!/bin/bash
set -e
if [ "$ENVIRONMENT" = "prod" ]; then
  gunicorn --workers=4 --bind=0.0.0.0:8081 factorial_hr.wsgi:application
elif [ "$ENVIRONMENT" = "qa" ]; then
  gunicorn --workers=4 --bind=0.0.0.0:8082 factorial_hr.wsgi:application
else
  python3 manage.py runserver 0.0.0.0:8000
fi