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

ENV DJANGO_SETTINGS_MODULE=juguetesonline.settings

# Collect static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "juguetesonline.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
