# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

COPY . .

# Установим pip и poetry, если есть pyproject.toml
RUN pip install --upgrade pip \
    && if [ -f pyproject.toml ]; then pip install poetry && poetry install --no-root; fi \
    && if [ -f req.txt ]; then pip install -r req.txt; fi

# Flask env vars
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["flask", "run"] 