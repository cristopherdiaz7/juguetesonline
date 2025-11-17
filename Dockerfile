FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# dependencias del sistema necesarias para mysqlclient y Pillow
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    libmariadb-dev-compat \
    pkg-config \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Ensure PyMySQL is installed even if requirements resolution had issues
RUN pip install --no-cache-dir PyMySQL

COPY . .

# Copy entrypoint and make it executable. The script will expand ${PORT} and
# run either the provided start command or gunicorn by default.
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN ln -s /entrypoint.sh /docker-entrypoint.sh || true

ENV DJANGO_SETTINGS_MODULE=juguetesonline.settings

# Collect static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Use an entrypoint script so any Railway-provided Start Command is executed via
# a shell (allowing ${PORT} expansion). If no command is provided, entrypoint
# will start gunicorn with ${PORT:-8000}.
ENTRYPOINT ["/entrypoint.sh"]
