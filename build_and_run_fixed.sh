#!/bin/bash

# Exit on any error
set -e

echo "===== Creating telemetry directories ====="
mkdir -p ./shared_telemetry/service-a
mkdir -p ./shared_telemetry/service-b
chmod -R 777 ./shared_telemetry
echo "✅ Telemetry directories created successfully"

echo "===== Stopping and removing existing containers ====="
docker stop service-a service-b load-balancer 2>/dev/null || true
docker rm service-a service-b load-balancer 2>/dev/null || true
echo "✅ Cleaned up existing containers"

echo "===== Building Docker images ====="
# Build Service A image
echo "Building service-a image..."
docker build -t nisheetdas1:service-a -f service.Dockerfile --build-arg SERVICE_NAME=service-a .

# Build Service B image
echo "Building service-b image..."
docker build -t nisheetdas1:service-b -f service.Dockerfile --build-arg SERVICE_NAME=service-b .

# Build Load Balancer image
echo "Building load-balancer image..."
docker build -t nisheetdas1:load-balancer -f loadbalancer/Dockerfile ./loadbalancer
echo "✅ Docker images built successfully"

echo "===== Creating Docker network ====="
# Create docker network if it doesn't exist
docker network inspect app-network >/dev/null 2>&1 || docker network create app-network
echo "✅ Network setup complete"

echo "===== Starting containers ====="
# Run Service A
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
  nisheetdas1:service-a

# Run Service B
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
  nisheetdas1:service-b

# Run Load Balancer
echo "Starting Load Balancer..."
docker run -d \
  --name load-balancer \
  --pull never \
  -p 8082:8082 \
  -e SERVICE_A_URL=http://service-a:8082 \
  -e SERVICE_B_URL=http://service-b:8082 \
  --network app-network \
  nisheetdas1:load-balancer

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
echo
echo "To test telemetry, try making a recommendation request:"
echo "  curl http://localhost:8083/recommend/123"
echo "  curl http://localhost:8084/recommend/123"
echo "  curl http://localhost:8082/recommend/123"
