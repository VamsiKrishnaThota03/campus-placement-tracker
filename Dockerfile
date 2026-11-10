# syntax=docker/dockerfile:1

FROM python:3.12-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_DEBUG=0 \
    MPLBACKEND=Agg

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY web ./web
COPY src ./src
COPY database ./database

RUN useradd --create-home --shell /usr/sbin/nologin app && chown -R app:app /app
USER app

WORKDIR /app/web
EXPOSE 5001

# Binds all interfaces inside the container; the published port is the security
# boundary (docker-compose.yml publishes to 127.0.0.1 only).
CMD ["gunicorn", "app:app", \
     "--bind", "0.0.0.0:5001", "--workers", "2", "--timeout", "120", \
     "--access-logfile", "-"]
