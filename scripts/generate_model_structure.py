#!/usr/bin/env python
"""
Script to generate the necessary model directory structure for the counter app.
This creates the models directory and any required model structure files.
"""
import os
import sys
import torch
import pickle
import random
import time
import numpy as np
from pathlib import Path

def ensure_model_directories():
    """Ensure all necessary model directories exist."""
    # Base path for the counter app
    base_path = Path(__file__).parent.parent / "cool_counters" / "counter"
    
    # Create models directory if it doesn't exist
    models_dir = base_path / "models"
    os.makedirs(models_dir, exist_ok=True)
    print(f"Created/ensured directory: {models_dir}")
    
    return models_dir

def generate_model_mappings(models_dir):
    """Generate model mappings file with required fields."""
    # Create mappings with all required fields
    user_id_map = {i: i for i in range(1, 101)}
    movie_id_map = {i: i for i in range(1, 501)}
    
    # Create reverse mappings needed by the model
    idx_to_user = {idx: user_id for user_id, idx in user_id_map.items()}
    idx_to_item = {idx: movie_id for movie_id, idx in movie_id_map.items()}
    
    # Create additional mappings
    item_to_idx = {movie_id: idx for idx, movie_id in idx_to_item.items()}
    user_to_idx = {user_id: idx for idx, user_id in idx_to_user.items()}
    
    mappings = {
        'user_id_map': user_id_map,
        'movie_id_map': movie_id_map,
        'idx_to_user': idx_to_user,
        'idx_to_item': idx_to_item,
        'item_to_idx': item_to_idx,
        'user_to_idx': user_to_idx,
        'timestamp': time.time(),
        'version': f"test-model-{random.randint(1, 1000)}"
    }
    
    # Save the mappings as a pickle file
    mappings_path = models_dir / "ncf_model_mappings.pkl"
    with open(mappings_path, 'wb') as f:
        pickle.dump(mappings, f)
    
    print(f"Created model mappings file: {mappings_path}")
    return mappings_path

def generate_model_file(models_dir):
    """Generate a simple PyTorch model file."""
    # Define a simple model class (similar to NCF model structure)
    class SimpleNCF(torch.nn.Module):
        def __init__(self, num_users=100, num_items=500, embed_dim=10):
            super(SimpleNCF, self).__init__()
            self.user_embedding = torch.nn.Embedding(num_users, embed_dim)
            self.item_embedding = torch.nn.Embedding(num_items, embed_dim)
            self.fc1 = torch.nn.Linear(embed_dim * 2, 20)
            self.fc2 = torch.nn.Linear(20, 10)
            self.fc3 = torch.nn.Linear(10, 1)
            self.relu = torch.nn.ReLU()
            
        def forward(self, user_indices, item_indices):
            user_embeds = self.user_embedding(user_indices)
            item_embeds = self.item_embedding(item_indices)
            x = torch.cat([user_embeds, item_embeds], dim=1)
            x = self.relu(self.fc1(x))
            x = self.relu(self.fc2(x))
            x = self.fc3(x)
            return x.squeeze()
    
    # Create model instance and initialize with random weights
    model = SimpleNCF()
    
    # Save the model
    model_path = models_dir / "ncf_model.pt"
    torch.save(model.state_dict(), model_path)
    
    print(f"Created model file: {model_path}")
    return model_path

def main():
    # Ensure all model directories exist
    models_dir = ensure_model_directories()
    
    # Generate model mappings file
    generate_model_mappings(models_dir)
    
    # Generate model file
    generate_model_file(models_dir)
    
    print("Model structure generation complete!")

if __name__ == "__main__":
    main()
