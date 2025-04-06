# Configurable A/B Testing Load Balancer

This load balancer distributes traffic between variants A and B of the inference service based on configurable weights.

## Features

- Configurable traffic distribution between variants
- Real-time metrics collection and reporting
- Configuration management via API
- Health check endpoint

## API Endpoints

- `/` - Main proxy endpoint that forwards requests to variant A or B
- `/metrics` - Provides metrics about traffic distribution and performance
- `/config` - Get or update the load balancer configuration
- `/health` - Health check endpoint
- `/reset_metrics` - Reset collected metrics

## Configuration

The configuration is stored in the app.py of the load balancer:

```json
{
    "variant_a": {
      "weight": 100,
      "service_url": "http://service-a:8082"
    },
    "variant_b": {
      "weight": 0,
      "service_url": "http://service-b:8082"
    },
    "monitoring": {
      "enabled": true,
      "log_level": "INFO"
    }
}
```

### Configuration Parameters

- `weight`: Percentage of traffic to direct to each variant (should sum to 100)
- `service_url`: URL of the variant's service
- `monitoring.enabled`: Whether to enable metrics collection and reporting
- `monitoring.log_level`: Log level (DEBUG, INFO, WARNING, ERROR)

## Updating Configuration

You can update the configuration via the `/config` endpoint:

```bash
curl --location 'http://localhost:8082/config' \
--header 'Content-Type: application/json' \
--data '{
    "variant_a": {
      "weight": 100,
      "service_url": "http://service-a:8082"
    },
    "variant_b": {
      "weight": 0,
      "service_url": "http://service-b:8082"
    },
    "monitoring": {
      "enabled": true,
      "log_level": "INFO"
    }
  }'
```

## Building and Running

### Build the Docker Image

```bash
./build.sh
```

### Run Locally

```bash
docker run -p 8082:8082 -v $(pwd)/config:/config loadbalancer:latest
```