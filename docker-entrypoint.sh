#!/bin/bash
set -e

# Collect static files
python canal/manage.py collectstatic --noinput

# Apply database migrations
python canal/manage.py migrate --noinput

# Start Daphne ASGI server
exec daphne -b 0.0.0.0 -p 8000 canal.asgi:application