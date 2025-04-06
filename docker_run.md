# Docker Run Commands for Telemetry

This document provides instructions for running the dockerized services with telemetry writing to separate folders on the host machine.

## Setup Telemetry Directories

Create separate telemetry directories for each service (run these commands from the project root directory):

```bash
mkdir -p ./shared_telemetry/service-a
mkdir -p ./shared_telemetry/service-b
chmod -R 777 ./shared_telemetry
```

Build Docker Images for Service A, Service B and Load Balancer
```bash
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
````

## Create the Docker Network
```bash
echo "===== Creating Docker network ====="
# Create docker network if it doesn't exist
docker network inspect app-network >/dev/null 2>&1 || docker network create app-network
echo "✅ Network setup complete"
```

## Run Service A

```bash
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
```

## Run Service B

```bash
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
```

## Run Load Balancer

```bash
docker run -d \
  --name load-balancer \
  --pull never \
  -p 8082:8082 \
  -e SERVICE_A_URL=http://service-a:8082 \
  -e SERVICE_B_URL=http://service-b:8082 \
  --network app-network \
  nisheetdas1:load-balancer
```

## Telemetry File Locations

With this setup:
- Service A will write telemetry files to `./shared_telemetry/service-a/`
- Service B will write telemetry files to `./shared_telemetry/service-b/`

## File Naming Convention

Telemetry files will be named following this pattern:
- `recommendation_telemetry_<service-name>_<date>_<AM/PM>.csv`

For example:
- `recommendation_telemetry_service-a_2025-04-05_AM.csv`
- `recommendation_telemetry_service-b_2025-04-05_AM.csv`

## Telemetry Data Format

Each telemetry file contains CSV data with the following columns:
- timestamp
- request_id
- user_id
- status_code
- model_used
- model_ref
- service_name
- num_recommendations
- recommended_movies
- error