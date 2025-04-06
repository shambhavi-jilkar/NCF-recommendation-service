#!/bin/bash

# Stop any running containers
echo "Stopping any existing containers..."
docker-compose down

# Generate initial test model weights
echo "Generating test model weights..."
python scripts/generate_test_weights.py --output_dir .

# Build and start the containers
echo "Building and starting containers..."
docker-compose up --build -d

# Print status
echo "Services are running!"
echo "Load balancer: http://localhost:8082"
echo "Service A: http://localhost:8083"
echo "Service B: http://localhost:8084"
echo ""
echo "To simulate weight updates, run:"
echo "  python scripts/generate_test_weights.py --output_dir . --service a"
echo "  python scripts/generate_test_weights.py --output_dir . --service b"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
