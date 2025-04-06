#!/bin/bash

# Set the image name and tag
IMAGE_NAME="loadbalancer"
TAG="latest"

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR" || exit 1

# Build the Docker image
echo "Building Docker image $IMAGE_NAME:$TAG..."
docker build -t "$IMAGE_NAME:$TAG" .

echo "Done! You can now push the image to your registry if needed."
echo "For local testing, the image is available as $IMAGE_NAME:$TAG"
