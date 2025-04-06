#!/usr/bin/env python3

"""
Debugging script for telemetry path resolution.
Execute it inside the Docker container to verify path resolution.
"""

import os
from pathlib import Path

# Simulate the TelemetryService path resolution
def debug_path_resolution():
    # Base path like in TelemetryService
    app_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    telemetry_dir = "data/telemetry"
    
    # Get the resolved path
    telemetry_path = app_dir / telemetry_dir
    
    print(f"Current working directory: {os.getcwd()}")
    print(f"__file__: {__file__}")
    print(f"app_dir: {app_dir}")
    print(f"Resolved telemetry path: {telemetry_path}")
    print(f"Does telemetry path exist? {os.path.exists(telemetry_path)}")
    print(f"Is telemetry path writable? {os.access(telemetry_path, os.W_OK)}")
    
    # Try to create a test file
    test_file = telemetry_path / "test_file.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("Test content")
        print(f"Successfully wrote to {test_file}")
    except Exception as e:
        print(f"Error writing to {test_file}: {e}")
    
    # Check environment variable
    service_name = os.environ.get('SERVICE_NAME', 'unknown')
    print(f"SERVICE_NAME environment variable: {service_name}")

if __name__ == "__main__":
    debug_path_resolution()
