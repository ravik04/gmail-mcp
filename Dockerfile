FROM python:3.12-slim

WORKDIR /app

# Install system deps (none required beyond default)

COPY pyproject.toml uv.lock README.md /app/
COPY src /app/src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["python", "-m", "gmail", "--mode", "api", "--port", "8080"]
