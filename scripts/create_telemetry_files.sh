#!/bin/bash

# Script to create next day's telemetry files and record the result
# The endpoint will ping the healthcheck URL automatically

# Configuration
APP_URL="http://128.2.205.118:8082"  # Update this to your application's URL
ENDPOINT="/telemetry/create-next-day"
LOG_FILE="./telemetry_creation_status.log"  # Path to the log file

# Get current timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "Creating next day's telemetry files..."

# Call the endpoint to create the files
RESPONSE=$(curl -s "$APP_URL$ENDPOINT")

# Extract the status from the response and write to log file
if echo "$RESPONSE" | grep -q "\"success\": true"; then
  echo "✅ Successfully created telemetry files for the next day."
  # Write success status to log file
  echo "$TIMESTAMP true" >> "$LOG_FILE"
  exit 0
else
  echo "❌ Failed to create telemetry files."
  echo "Error response: $RESPONSE"
  # Write failure status to log file
  echo "$TIMESTAMP false" >> "$LOG_FILE"
  exit 1
fi
