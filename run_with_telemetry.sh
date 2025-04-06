#!/bin/bash

# Exit on any error
set -e

echo "Setting up telemetry directories..."
mkdir -p ./shared_telemetry/service-a
mkdir -p ./shared_telemetry/service-b
chmod -R 777 ./shared_telemetry
echo "✅ Telemetry directories created successfully"

# Clean up existing containers if they exist
echo "Cleaning up any existing containers..."
docker rm -f service-a service-b load-balancer 2>/dev/null || true

# Create docker network if it doesn't exist
docker network inspect app-network >/dev/null 2>&1 || docker network create app-network
echo "✅ Network setup complete"

echo "Starting Service A..."
docker run -d \
  --name service-a \
  --pull never \
  -p 8083:8082 \
  -v $(pwd)/model-weights-a:/app/model-data \
  -v $(pwd)/shared_telemetry/service-a:/app/data/telemetry \
  -e SERVICE_NAME=service-a \
  -e MODEL_FOLDER=/app/model-data \
  --network app-network \
  group-project-s25-the_call_of_the_wild-service-a:latest

echo "Starting Service B..."
docker run -d \
  --name service-b \
  --pull never \
  -p 8084:8082 \
  -v $(pwd)/model-weights-b:/app/model-data \
  -v $(pwd)/shared_telemetry/service-b:/app/data/telemetry \
  -e SERVICE_NAME=service-b \
  -e MODEL_FOLDER=/app/model-data \
  --network app-network \
  group-project-s25-the_call_of_the_wild-service-b:latest

echo "Starting Load Balancer..."
docker run -d \
  --name load-balancer \
  --pull never \
  -p 8082:8082 \
  --network app-network \
  group-project-s25-the_call_of_the_wild-load-balancer:latest

echo "✅ All services started successfully!"
echo 
echo "Services:"
echo "  • Load Balancer: http://localhost:8082"
echo "  • Service A:     http://localhost:8083"
echo "  • Service B:     http://localhost:8084"
echo
echo "Telemetry files will be written to:"
echo "  • Service A: $(pwd)/shared_telemetry/service-a/"
echo "  • Service B: $(pwd)/shared_telemetry/service-b/"
