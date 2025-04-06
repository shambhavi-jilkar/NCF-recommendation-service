#!/usr/bin/env python
"""
Script to generate test model weights files for testing the weight updater.
"""
import os
import sys
import pickle
import torch
import numpy as np
import random
import time
import argparse

def generate_test_model_pt(output_dir, model_name="ncf_model.pt"):
    """Generate a test PyTorch model file."""
    # Create a simple model
    class SimpleModel(torch.nn.Module):
        def __init__(self):
            super(SimpleModel, self).__init__()
            self.fc1 = torch.nn.Linear(10, 5)
            self.fc2 = torch.nn.Linear(5, 1)
            
        def forward(self, x):
            x = torch.relu(self.fc1(x))
            x = self.fc2(x)
            return x
    
    # Initialize the model with random weights
    model = SimpleModel()
    
    # Save the model
    output_path = os.path.join(output_dir, model_name)
    torch.save(model.state_dict(), output_path)
    print(f"Generated PyTorch model: {output_path}")
    return output_path

def generate_test_mappings_pkl(output_dir, mappings_name="ncf_model_mappings.pkl"):
    """Generate test mappings pickle file with all required keys."""
    # Create mappings with all required fields
    user_id_map = {i: i for i in range(100)}
    item_id_map = {i: i for i in range(500)}
    
    # Create reverse mappings needed by the model
    idx_to_user = {idx: user_id for user_id, idx in user_id_map.items()}
    idx_to_item = {idx: item_id for item_id, idx in item_id_map.items()}
    
    # Create additional mappings
    item_to_idx = {item_id: idx for idx, item_id in idx_to_item.items()}
    user_to_idx = {user_id: idx for idx, user_id in idx_to_user.items()}
    
    mappings = {
        'user_id_map': user_id_map,
        'movie_id_map': item_id_map,
        'idx_to_user': idx_to_user,
        'idx_to_item': idx_to_item,
        'item_to_idx': item_to_idx,
        'user_to_idx': user_to_idx,
        'timestamp': time.time(),
        'version': f"test-{random.randint(1, 1000)}"
    }
    
    # Save mappings
    output_path = os.path.join(output_dir, mappings_name)
    with open(output_path, 'wb') as f:
        pickle.dump(mappings, f)
    print(f"Generated mappings file: {output_path}")
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Generate test model weight files')
    parser.add_argument('--output_dir', type=str, required=True, 
                      help='Directory where model files will be saved')
    parser.add_argument('--service', type=str, choices=['a', 'b', 'both'], default='both',
                      help='Which service to generate weights for (a, b, or both)')
    
    args = parser.parse_args()
    
    if args.service in ['a', 'both']:
        output_dir = os.path.join(args.output_dir, 'model-weights-a')
        os.makedirs(output_dir, exist_ok=True)
        generate_test_model_pt(output_dir)
        generate_test_mappings_pkl(output_dir)
        
    if args.service in ['b', 'both']:
        output_dir = os.path.join(args.output_dir, 'model-weights-b')
        os.makedirs(output_dir, exist_ok=True)
        generate_test_model_pt(output_dir)
        generate_test_mappings_pkl(output_dir)
        
    print("Done generating test model weights.")

if __name__ == "__main__":
    main()
