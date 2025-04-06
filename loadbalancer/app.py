import os
import time
import json
import random
import logging
import requests
from flask import Flask, request, jsonify, Response
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ab-loadbalancer')

app = Flask(__name__)

# Get service URLs from environment variables
SERVICE_A_URL = os.environ.get('SERVICE_A_URL', 'http://128.2.205.118:8083')
SERVICE_B_URL = os.environ.get('SERVICE_B_URL', 'http://128.2.205.118:8084')

# Load balancer configuration
DEFAULT_CONFIG = {
    "variant_a": {
        "weight": 50,
        "service_url": SERVICE_A_URL
    },
    "variant_b": {
        "weight": 50,
        "service_url": SERVICE_B_URL
    },
    "monitoring": {
        "enabled": True,
        "log_level": "INFO"
    }
}

# In-memory metrics
metrics = {
    "requests": {
        "total": 0,
        "variant_a": 0,
        "variant_b": 0,
        "errors": 0
    },
    "latency": {
        "variant_a": [],
        "variant_b": []
    }
}

def load_config():
    """Load the configuration from file or use default"""
    return DEFAULT_CONFIG

# Global configuration
config = load_config()

# Set log level from config
if config["monitoring"]["log_level"]:
    logging.getLogger().setLevel(config["monitoring"]["log_level"])

def select_variant():
    """Select a variant based on the configured weights"""
    weight_a = config["variant_a"]["weight"]
    weight_b = config["variant_b"]["weight"]
    
    # Normalize weights if they don't add up to 100
    total_weight = weight_a + weight_b
    if total_weight != 100:
        weight_a = (weight_a / total_weight) * 100
        weight_b = (weight_b / total_weight) * 100
    
    # Random selection based on weights
    rand_val = random.uniform(0, 100)
    if rand_val <= weight_a:
        return "variant_a"
    else:
        return "variant_b"

def forward_request(variant, path, request_data):
    """Forward the request to the selected variant"""
    start_time = time.time()
    
    # Get the base URL for the selected variant
    base_url = config[variant]["service_url"]
    target_url = f"{base_url}{path}"
    
    # Log request details
    logger.info(f"Forwarding request to {variant}: {target_url}")
    
    # Extract headers to forward (excluding hop-by-hop headers)
    headers_to_forward = {
        k: v for k, v in request.headers.items() 
        if k.lower() not in ['host', 'connection', 'content-length', 'transfer-encoding']
    }
    
    try:
        # Forward the request with the same method, headers, and data
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers_to_forward,
            params=request.args,
            data=request_data,
            cookies=request.cookies,
            timeout=30  # 30 second timeout
        )
        
        # Update metrics
        metrics["requests"]["total"] += 1
        metrics["requests"][variant] += 1
        
        # Record latency
        latency = time.time() - start_time
        metrics["latency"][variant].append(latency)
        # Keep only the last 1000 latency records
        if len(metrics["latency"][variant]) > 1000:
            metrics["latency"][variant] = metrics["latency"][variant][-1000:]
        
        # Log response info
        logger.info(f"Response from {variant}: status={response.status_code}, latency={latency:.3f}s")
        
        # Return the response with the same status code, headers, and content
        return Response(
            response.content,
            status=response.status_code,
            headers={k: v for k, v in response.headers.items() 
                     if k.lower() not in ['transfer-encoding']}
        )
        
    except RequestException as e:
        # Handle request errors
        logger.error(f"Error forwarding request to {variant}: {str(e)}")
        metrics["requests"]["errors"] += 1
        return jsonify({
            "error": "Failed to reach service",
            "details": str(e)
        }), 503

@app.route('/status')
def status_check():
    """Status check endpoint"""
    # Check both services
    services_status = {}
    
    try:
        response_a = requests.get(f"{config['variant_a']['service_url']}/status", timeout=5)
        services_status["service_a"] = {
            "status": "up" if response_a.status_code == 200 else "degraded",
            "status_code": response_a.status_code,
            "response": response_a.text
        }
    except Exception as e:
        services_status["service_a"] = {
            "status": "down",
            "error": str(e)
        }
    
    try:
        response_b = requests.get(f"{config['variant_b']['service_url']}/status", timeout=5)
        services_status["service_b"] = {
            "status": "up" if response_b.status_code == 200 else "degraded",
            "status_code": response_b.status_code,
            "response": response_b.text
        }
    except Exception as e:
        services_status["service_b"] = {
            "status": "down",
            "error": str(e)
        }
    
    # Determine overall status
    if services_status["service_a"]["status"] == "up" and services_status["service_b"]["status"] == "up":
        overall_status = "OK"
        status_code = 200
    elif services_status["service_a"]["status"] == "up" or services_status["service_b"]["status"] == "up":
        overall_status = "DEGRADED - Some services unavailable"
        status_code = 200
    else:
        overall_status = "CRITICAL - All services down"
        status_code = 500
    
    return Response(overall_status, status=status_code)

@app.route('/metrics')
def get_metrics():
    """Endpoint to retrieve current metrics"""
    if not config["monitoring"]["enabled"]:
        return jsonify({"error": "Monitoring is disabled"}), 403
    
    # Calculate average latency for each variant
    avg_latency_a = sum(metrics["latency"]["variant_a"]) / max(len(metrics["latency"]["variant_a"]), 1)
    avg_latency_b = sum(metrics["latency"]["variant_b"]) / max(len(metrics["latency"]["variant_b"]), 1)
    
    # Return formatted metrics
    return jsonify({
        "total_requests": metrics["requests"]["total"],
        "variant_a_requests": metrics["requests"]["variant_a"],
        "variant_b_requests": metrics["requests"]["variant_b"],
        "errors": metrics["requests"]["errors"],
        "variant_a_percentage": (metrics["requests"]["variant_a"] / max(metrics["requests"]["total"], 1)) * 100,
        "variant_b_percentage": (metrics["requests"]["variant_b"] / max(metrics["requests"]["total"], 1)) * 100,
        "variant_a_avg_latency": avg_latency_a,
        "variant_b_avg_latency": avg_latency_b,
        "config": config
    })

@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    """Endpoint to get or update configuration"""
    global config
    
    if request.method == 'GET':
        return jsonify(config)
    
    elif request.method == 'POST':
        try:
            new_config = request.json
            
            # Validate new config
            if "variant_a" not in new_config or "variant_b" not in new_config:
                return jsonify({"error": "Invalid configuration: missing variant data"}), 400
            
            # Update config
            config = new_config
            
            # Update log level if changed
            if "monitoring" in config and "log_level" in config["monitoring"]:
                logging.getLogger().setLevel(config["monitoring"]["log_level"])
            
            logger.info("Configuration updated")
            return jsonify({"message": "Configuration updated successfully", "config": config})
            
        except Exception as e:
            logger.error(f"Error updating configuration: {str(e)}")
            return jsonify({"error": f"Failed to update configuration: {str(e)}"}), 400

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/reset_metrics', methods=['POST'])
def reset_metrics():
    """Reset the metrics counters"""
    global metrics
    metrics = {
        "requests": {
            "total": 0,
            "variant_a": 0,
            "variant_b": 0,
            "errors": 0
        },
        "latency": {
            "variant_a": [],
            "variant_b": []
        }
    }
    return jsonify({"message": "Metrics reset successfully"})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    """Main proxy endpoint that handles all requests"""
    # Select variant A or B based on configured weights
    variant = select_variant()
    
    # Get request data
    request_data = request.get_data()
    
    # Forward the request to the selected variant
    return forward_request(variant, f"/{path}", request_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8082))
    logger.info(f"Starting A/B testing load balancer on port {port}")
    logger.info(f"Variant A weight: {config['variant_a']['weight']}%, URL: {config['variant_a']['service_url']}")
    logger.info(f"Variant B weight: {config['variant_b']['weight']}%, URL: {config['variant_b']['service_url']}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
