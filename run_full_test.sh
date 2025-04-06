#!/bin/bash

# Exit on any error
set -e

echo "============================================="
echo "Full Test of Django Application with Docker Containers"
echo "============================================="

# Generate model structure
echo "Generating model structure..."
python scripts/generate_model_structure.py

# Test local setup
echo "Testing local setup..."
./test_local_setup.sh

# Check if the containers are working properly
echo "Checking container health..."
CONTAINERS_HEALTHY=true

# Test Load Balancer
echo "Testing Load Balancer..."
if ! curl -s --max-time 5 http://localhost:8082/status | grep -q "OK"; then
  echo "FAIL: Load Balancer health check failed"
  CONTAINERS_HEALTHY=false
else
  echo "PASS: Load Balancer is healthy"
fi

# Test Service A
echo "Testing Service A..."
if ! curl -s --max-time 5 http://localhost:8083/status | grep -q "OK"; then
  echo "FAIL: Service A health check failed"
  CONTAINERS_HEALTHY=false
else
  echo "PASS: Service A is healthy"
fi

# Test Service B
echo "Testing Service B..."
if ! curl -s --max-time 5 http://localhost:8084/status | grep -q "OK"; then
  echo "FAIL: Service B health check failed"
  CONTAINERS_HEALTHY=false
else
  echo "PASS: Service B is healthy"
fi

# Test model weight updates
echo "Testing model weight updates..."
cd scripts
./test_weight_updates.sh
cd ..

# Print conclusion
if [ "$CONTAINERS_HEALTHY" = true ]; then
  echo "============================================="
  echo "TEST SUMMARY: All containers are working properly!"
  echo "============================================="
  echo ""
  echo "Next steps to push to DockerHub:"
  echo "1. Login to DockerHub: docker login -u nisheetdas1"
  echo "2. Build and push images: ./build_and_push_dockerhub.sh"
  echo "3. Run from DockerHub: ./run_services_dockerhub.sh"
  echo ""
else
  echo "============================================="
  echo "TEST SUMMARY: Some containers are not working properly!"
  echo "Check the logs for more details: docker-compose logs"
  echo "============================================="
  exit 1
fi
