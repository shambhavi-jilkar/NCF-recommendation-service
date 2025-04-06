#!/bin/bash

# Set your DockerHub username here
DOCKERHUB_USERNAME="nisheetdas1"

# Image names and tags
INFERENCE_IMAGE_NAME="inference-service"
LOADBALANCER_IMAGE_NAME="inference-loadbalancer"
TAG="latest"

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR" || exit 1

echo "Building and pushing Docker images with DockerHub username: $DOCKERHUB_USERNAME"

# Check if DockerHub username has been set
if [ "$DOCKERHUB_USERNAME" = "YOUR_DOCKERHUB_USERNAME" ]; then
    echo "Error: Please edit this script to set your DockerHub username"
    exit 1
fi

# Check if user is logged in to Docker Hub
echo "Checking Docker Hub login status..."
docker info | grep Username > /dev/null
if [ $? -ne 0 ]; then
    echo "You are not logged in to Docker Hub. Please login:"
    docker login
    if [ $? -ne 0 ]; then
        echo "Docker Hub login failed. Exiting."
        exit 1
    fi
fi

# Build and push inference service image
echo "Building inference service image..."
docker build -t "$INFERENCE_IMAGE_NAME:$TAG" -f service.Dockerfile .
if [ $? -ne 0 ]; then
    echo "Error building inference service image. Exiting."
    exit 1
fi

echo "Tagging inference service image for DockerHub..."
docker tag "$INFERENCE_IMAGE_NAME:$TAG" "$DOCKERHUB_USERNAME/$INFERENCE_IMAGE_NAME:$TAG"
if [ $? -ne 0 ]; then
    echo "Error tagging inference service image. Exiting."
    exit 1
fi

echo "Pushing inference service image to DockerHub..."
docker push "$DOCKERHUB_USERNAME/$INFERENCE_IMAGE_NAME:$TAG"
if [ $? -ne 0 ]; then
    echo "Error pushing inference service image. Exiting."
    exit 1
fi

# Build and push load balancer image
echo "Building load balancer image..."
cd loadbalancer || exit 1
docker build -t "$LOADBALANCER_IMAGE_NAME:$TAG" .
if [ $? -ne 0 ]; then
    echo "Error building load balancer image. Exiting."
    exit 1
fi

echo "Tagging load balancer image for DockerHub..."
docker tag "$LOADBALANCER_IMAGE_NAME:$TAG" "$DOCKERHUB_USERNAME/$LOADBALANCER_IMAGE_NAME:$TAG"
if [ $? -ne 0 ]; then
    echo "Error tagging load balancer image. Exiting."
    exit 1
fi

echo "Pushing load balancer image to DockerHub..."
docker push "$DOCKERHUB_USERNAME/$LOADBALANCER_IMAGE_NAME:$TAG"
if [ $? -ne 0 ]; then
    echo "Error pushing load balancer image. Exiting."
    exit 1
fi

cd "$SCRIPT_DIR" || exit 1

echo "All images built and pushed successfully to DockerHub!"
echo ""
echo "To use these images in Kubernetes:"
echo "1. Edit the Kubernetes manifests in the k8s/ directory to use:"
echo "   - $DOCKERHUB_USERNAME/$INFERENCE_IMAGE_NAME:$TAG"
echo "   - $DOCKERHUB_USERNAME/$LOADBALANCER_IMAGE_NAME:$TAG"
echo ""
echo "2. Or run the update_image_names.sh script which will update them automatically"
