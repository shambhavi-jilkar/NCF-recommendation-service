#!/usr/bin/env python
"""
Script to debug model loading by examining PredictionService and its requirements.
"""
import os
import sys
import pickle
import torch
import traceback
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def debug_prediction_service():
    print("Debugging PredictionService model loading...")
    
    try:
        # Try to import the PredictionService
        from cool_counters.counter.services.PredictionService import PredictionService
        print("Successfully imported PredictionService")
        
        # Create an instance
        prediction_service = PredictionService()
        print(f"Created PredictionService instance")
        print(f"Models path: {prediction_service.MODELS_PATH}")
        
        # Check if mappings file exists
        mappings_path = prediction_service.MODELS_PATH / "ncf_model_mappings.pkl"
        if os.path.exists(mappings_path):
            print(f"Found mappings file at {mappings_path}")
            
            # Load and print the mappings structure
            with open(mappings_path, 'rb') as f:
                mappings = pickle.load(f)
            print("Mappings structure:")
            print(f"  Keys: {list(mappings.keys())}")
            
            # Check for required keys
            required_keys = ['user_id_map', 'movie_id_map', 'idx_to_user', 'idx_to_item']
            missing_keys = [key for key in required_keys if key not in mappings]
            
            if missing_keys:
                print(f"WARNING: Missing required keys in mappings: {missing_keys}")
            else:
                print("All required keys present in mappings")
                
            # Show sample data
            for key in mappings:
                if isinstance(mappings[key], dict):
                    sample_items = dict(list(mappings[key].items())[:3])
                    print(f"  {key}: {sample_items} ... (and {len(mappings[key]) - 3} more items)")
                else:
                    print(f"  {key}: {mappings[key]}")
        else:
            print(f"Mappings file not found at {mappings_path}")
            
        # Check if model file exists
        model_path = prediction_service.MODELS_PATH / "ncf_model.pt"
        if os.path.exists(model_path):
            print(f"Found model file at {model_path}")
            
            # Try to load the model
            print("Attempting to load model...")
            model = prediction_service._load_ncf_model()
            
            if model is None:
                print("Failed to load model: model is None")
            else:
                print("Successfully loaded model!")
                print(f"Model type: {type(model)}")
        else:
            print(f"Model file not found at {model_path}")
            
    except Exception as e:
        print(f"Error debugging PredictionService: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_prediction_service()
