#!/bin/bash

# Exit on any error
set -e

echo "Preparing model weights directories..."

# Create the model weights directories if they don't exist
mkdir -p model-weights-a model-weights-b

# Create the model files
echo "Creating model files that match the NCF class structure..."
python -c "
import torch
import torch.nn as nn
import pickle
import os

# Ensure directories exist
os.makedirs('model-weights-a', exist_ok=True)
os.makedirs('model-weights-b', exist_ok=True)

# Create a model that matches the structure of the NCF class
class NCF(nn.Module):
    def __init__(self, num_users=100, num_items=500, embed_dim=32, linear_dims=None):
        super(NCF, self).__init__()
        if linear_dims is None:
            linear_dims = [64, 32, 16, 8]
        self.user_embedding = nn.Embedding(num_users, embed_dim)
        self.item_embedding = nn.Embedding(num_items, embed_dim)
        
        # Add linear + relu layers
        layers = []
        input_dim = 2 * embed_dim
        output_dim = 1
        for dim in linear_dims:
            layers.append(nn.Linear(input_dim, dim))
            layers.append(nn.ReLU())
            input_dim = dim

        layers.append(nn.Linear(input_dim, output_dim))
        self.mlp = nn.Sequential(*layers)

    def forward(self, user, item):
        user_emb = self.user_embedding(user)
        item_emb = self.item_embedding(item)
        x = torch.cat([user_emb, item_emb], dim=1)
        return self.mlp(x).squeeze()

# Parameters
num_users = 100
num_items = 500
embed_dim = 32
linear_dims = [64, 32, 16, 8]  # Match the structure in neural_cf.py

# Create user and movie ID mappings
user_id_map = {i: i for i in range(1, num_users+1)}
movie_id_map = {i: i for i in range(1, num_items+1)}

# Create reverse mappings needed by the model
idx_to_user = {idx: user_id for user_id, idx in user_id_map.items()}
idx_to_item = {idx: movie_id for movie_id, idx in movie_id_map.items()}

# Create additional mappings
item_to_idx = {movie_id: idx for idx, movie_id in idx_to_item.items()}
user_to_idx = {user_id: idx for idx, user_id in idx_to_user.items()}

# Create mappings for service A
mappings_a = {
    'user_id_map': user_id_map,
    'movie_id_map': movie_id_map,
    'idx_to_user': idx_to_user,
    'idx_to_item': idx_to_item,
    'item_to_idx': item_to_idx,
    'user_to_idx': user_to_idx,
    'version': 'service-a-v1'
}

# Save mappings for service A
with open('model-weights-a/ncf_model_mappings.pkl', 'wb') as f:
    pickle.dump(mappings_a, f)
print('Created model-weights-a/ncf_model_mappings.pkl')

# Create model for service A
model_a = NCF(num_users, num_items, embed_dim, linear_dims)
torch.save(model_a.state_dict(), 'model-weights-a/ncf_model.pt')
print('Created model-weights-a/ncf_model.pt')

# Create mappings for service B (same structure, different version)
mappings_b = {
    'user_id_map': user_id_map,
    'movie_id_map': movie_id_map,
    'idx_to_user': idx_to_user,
    'idx_to_item': idx_to_item,
    'item_to_idx': item_to_idx,
    'user_to_idx': user_to_idx,
    'version': 'service-b-v1'
}

# Save mappings for service B
with open