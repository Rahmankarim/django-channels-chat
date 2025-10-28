# Build stage
FROM python:3.9-slim as builder

# Prevent Python from buffering stdout/stderr and from writing pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Install build dependencies
# changes made
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements /build/requirements
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements/development.txt \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements/development.txt

# Final stage
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/venv/bin:$PATH"

WORKDIR /app

# Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && python -m venv /venv

# Copy wheels and install dependencies
COPY --from=builder /build/wheels /wheels
RUN /venv/bin/pip install --no-cache /wheels/*

# Copy project files
COPY . .

# Create directory for static files
RUN mkdir -p /app/staticfiles

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app /venv
USER appuser

# Expose Daphne port
EXPOSE 8000

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/chat/ || exit 1

# Start script
COPY --chown=appuser:appuser docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
