#!/bin/sh
set -e

# ensure working dir
cd /app || true

# If a command was provided (e.g. Railway Start Command), execute it through a shell
# so environment variables like ${PORT} are expanded. Otherwise start gunicorn.
if [ "$#" -gt 0 ]; then
  cmd="$*"
  exec sh -c "exec $cmd"
else
  # Run database migrations and collectstatic at container start.
  # This ensures the remote deployment applies migrations automatically.
  echo "-> Running migrations"
  python manage.py migrate --noinput || echo "migrate failed"
  echo "-> Collecting static files"
  python manage.py collectstatic --noinput || echo "collectstatic failed"

  exec gunicorn juguetesonline.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 3
fi
