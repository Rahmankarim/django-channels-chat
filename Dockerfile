FROM python:3.9-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install system deps required to build some Python packages (psycopg2, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements/development.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# Copy project
COPY . .

# Expose Daphne port
EXPOSE 8000

# Default command: run migrations then start Daphne (ASGI server for Channels)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "canal.asgi:application"]
