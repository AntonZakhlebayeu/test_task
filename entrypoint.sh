#!/bin/bash
set -e

python manage.py migrate
python manage.py collectstatic --noinput

if [ -n "$DJANGO_ADMIN_USERNAME" ] && [ -n "$DJANGO_ADMIN_EMAIL" ] && [ -n "$DJANGO_ADMIN_PASSWORD" ]; then
  echo "from django.contrib.auth import get_user_model; User = get_user_model(); \
User.objects.filter(username='$DJANGO_ADMIN_USERNAME').exists() or \
User.objects.create_superuser('$DJANGO_ADMIN_USERNAME', '$DJANGO_ADMIN_EMAIL', '$DJANGO_ADMIN_PASSWORD')" \
  | python manage.py shell
fi

exec watchmedo auto-restart \
  --directory=. \
  --pattern=*.py \
  --recursive \
  -- \
  gunicorn \
  --bind 0.0.0.0:${APPLICATION_PORT:-8000} \
  config.wsgi:application \
  --reload
