#!/bin/bash

# Get environment variables
MODEL_FOLDER=${MODEL_FOLDER:-"/app/model-data"}
SERVICE_NAME=${SERVICE_NAME:-"unknown"}

echo "Starting service: $SERVICE_NAME"
echo "Model folder: $MODEL_FOLDER"

# Ensure model folder exists
echo "Ensuring model folder exists: $MODEL_FOLDER"
mkdir -p $MODEL_FOLDER

# Start the Django application with Gunicorn
echo "Starting the Django application with Gunicorn"
cd /app
export PYTHONPATH=/app:$PYTHONPATH

# The integrated weight updater will run as part of the Django application
gunicorn --bind 0.0.0.0:8082 --workers 2 cool_counters.wsgi:application
