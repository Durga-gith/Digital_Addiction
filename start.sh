#!/bin/bash
set -e

# Print current directory and environment info for debugging
echo "Current directory: $(pwd)"
echo "PYTHONPATH: $PYTHONPATH"
echo "Listing directory contents:"
ls -la

# Run database migrations
echo "Running database migrations..."
# Check if alembic.ini exists
if [ ! -f "alembic.ini" ]; then
    echo "ERROR: alembic.ini not found!"
    exit 1
fi

# Run alembic, but allow it to fail without crashing the container immediately
# This helps debug connection issues
alembic upgrade head || {
    echo "WARNING: Database migration failed. Starting application anyway..."
    echo "Check your DATABASE_URL and database connectivity."
}

# Start the application
echo "Starting application..."
# Use PORT env var if set, otherwise default to 8000
PORT="${PORT:-8000}"
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
