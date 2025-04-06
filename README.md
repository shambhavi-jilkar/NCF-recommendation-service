# Inference Service with A/B Testing

This project provides a complete setup for A/B testing of ML models in a Kubernetes environment. It includes containerized services, a configurable load balancer, and automatic model reloading.

## Features

- **Configurable Traffic Distribution**: Set the exact percentage of traffic for each variant
- **Model Hot-Reloading**: Update models without restarting services
- **Real-time Metrics**: Monitor performance and usage statistics
- **Zero-Downtime Updates**: Change configuration without service interruption
- **DockerHub Integration**: Build, push, and deploy from DockerHub
- **Easy Rollbacks**: Multiple rollback strategies for quick recovery

## Quick Start Guide

### Option 1: Local Deployment

```bash
# Initialize model directories with current models
./initialize_models.sh

# Build and deploy to Kubernetes (using local images)
./deploy.sh
```

### Option 2: DockerHub Deployment

```bash
# 1. Edit these files to set your DockerHub username
#    - build_and_push.sh
#    - update_image_names.sh
#    - deploy_from_dockerhub.sh
#    - rollback.sh

# 2. Build and push images to DockerHub
./build_and_push.sh

# 3. Deploy to Kubernetes using DockerHub images
./deploy_from_dockerhub.sh
```

### Accessing the Service

```bash
# Forward the load balancer port
kubectl port-forward svc/inference-loadbalancer 8082:8082

# Make a request
curl http://localhost:8082/recommend/123

# View traffic metrics
curl http://localhost:8082/metrics
```

### Adjusting Traffic Distribution

```bash
curl -X POST http://localhost:8082/config \
  -H "Content-Type: application/json" \
  -d '{
    "variant_a": {
      "weight": 80,
      "service_url": "http://inference-service-a:8082"
    },
    "variant_b": {
      "weight": 20,
      "service_url": "http://inference-service-b:8082"
    },
    "monitoring": {
      "enabled": true,
      "log_level": "INFO"
    }
  }'
```

### Performing a Rollback

Use the included rollback script for easy rollbacks:

```bash
# Redirect 100% traffic to variant A (fastest rollback)
./rollback.sh traffic

# Roll back deployment to previous version
./rollback.sh deployment

# Roll back to a specific version
./rollback.sh version v1.0.0
```

## Architecture

```
                 ┌─────────────────┐
                 │                 │
 Client ────────►│  Load Balancer  │
                 │                 │
                 └────────┬────────┘
                          │
                          ▼
         ┌────────────────┴────────────────┐
         │                                 │
         ▼                                 ▼
┌─────────────────┐               ┌─────────────────┐
│                 │               │                 │
│  Variant A (%)  │               │  Variant B (%)  │
│                 │               │                 │
└─────────────────┘               └─────────────────┘
```

Each variant has:
- Its own Kubernetes deployment
- A dedicated service
- A persistent volume for model files
- A file watcher that automatically reloads models when changed

## Directory Structure

- **`loadbalancer/`**: Custom load balancer application

## Components and Files

### Core Components

- **Inference Service**: Containerized ML inference application
- **Load Balancer**: Custom traffic distribution service
- **File Watcher**: Monitors model files and triggers reloading

### Key Scripts

- **`initialize_models.sh`**: Copy current models to A/B directories
- **`build_image.sh`** & **`loadbalancer/build.sh`**: Build Docker images
- **`build_and_push.sh`**: Build and push images to DockerHub
- **`deploy.sh`**: Deploy using local images
- **`deploy_from_dockerhub.sh`**: Deploy using DockerHub images
- **`rollback.sh`**: Perform various rollback operations
