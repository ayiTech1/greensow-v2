#!/bin/sh

# Exit if any command fails
set -e

# Wait for MySQL to be available
echo "Waiting for MySQL to be available..."
until nc -z "${DB_HOST:-db}" "${DB_PORT:-3306}"; do
  echo "Waiting for MySQL at ${DB_HOST:-db}:${DB_PORT:-3306}..."
  sleep 2
done
echo "MySQL is up!"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the server
exec "$@"
