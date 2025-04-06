#!/bin/bash

# Exit on any error
set -e

echo "Testing weight update mechanism..."

# First, let's wait for all services to be up
echo "Waiting for services to start..."
sleep 10

# Generate new weights for Service A
echo "Generating new test weights for Service A..."
python generate_test_weights.py --output_dir .. --service a

# Wait a bit for the weight updater to check for changes
echo "Waiting for Service A to detect changes (20 seconds)..."
sleep 20

# Check logs for Service A
echo "Checking Service A logs for weight updates..."
docker-compose logs --tail=100 service-a | grep -i "model successfully reloaded" && echo "Service A successfully reloaded the model!" || echo "Service A did not reload the model!"

# Generate new weights for Service B
echo "Generating new test weights for Service B..."
python generate_test_weights.py --output_dir .. --service b

# Wait a bit for the weight updater to check for changes
echo "Waiting for Service B to detect changes (20 seconds)..."
sleep 20

# Check logs for Service B
echo "Checking Service B logs for weight updates..."
docker-compose logs --tail=100 service-b | grep -i "model successfully reloaded" && echo "Service B successfully reloaded the model!" || echo "Service B did not reload the model!"

echo "Testing complete. Check the output above to see if the weight update mechanism is working."
