import json
import os
import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer

# Check if CUDA is available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# Load the model
model_name = 'all-MiniLM-L6-v2'  # A good balance between performance and speed
model = SentenceTransformer(model_name, device=device)
print(f"Loaded model: {model_name}")

# Load property listings
try:
    with open('listings.json', 'r') as f:
        listings = json.load(f)
    print(f"Loaded {len(listings)} property listings")
except FileNotFoundError:
    print("Error: listings.json not found")
    exit(1)

# Prepare text for embedding
documents = []
id_map = {}

for i, listing in enumerate(listings):
    # Create a rich text representation of each property
    text = f"Property ID: {listing['id']}\n"
    if 'title' in listing:
        text += f"Title: {listing['title']}\n"
    if 'address' in listing:
        text += f"Address: {listing['address']}\n"
    if 'price' in listing:
        if 'status' in listing and listing['status'] == 'For Rent':
            text += f"Price: £{listing['price']} per {'month' if 'rentPeriod' in listing and listing['rentPeriod'] == 'monthly' else 'week'}\n"
        else:
            text += f"Price: £{listing['price']}\n"
    if 'bedrooms' in listing:
        text += f"Bedrooms: {listing['bedrooms']}\n"
    if 'bathrooms' in listing:
        text += f"Bathrooms: {listing['bathrooms']}\n"
    if 'type' in listing:
        text += f"Property Type: {listing['type']}\n"
    if 'area' in listing:
        text += f"Area: {listing['area']}\n"
    if 'status' in listing:
        text += f"Status: {listing['status']}\n"
    if 'description' in listing:
        text += f"Description: {listing['description']}\n"
    if 'features' in listing and isinstance(listing['features'], list):
        text += f"Features: {', '.join(listing['features'])}\n"
    
    documents.append(text)
    id_map[i] = listing['id']

print(f"Prepared {len(documents)} documents for embedding")

# Generate embeddings
print("Generating embeddings...")
embeddings = model.encode(documents, show_progress_bar=True)
print(f"Generated embeddings with shape: {embeddings.shape}")

# Normalize embeddings for cosine similarity
faiss.normalize_L2(embeddings)

# Create FAISS index
index = faiss.IndexFlatIP(embeddings.shape[1])  # Inner product for cosine similarity with normalized vectors
index.add(embeddings)
print("Created FAISS index")

# Save the index and ID mapping
faiss.write_index(index, "listings.index")
with open("id_map.json", "w") as f:
    json.dump(id_map, f)

print("Saved index to listings.index and ID mapping to id_map.json")

# Test the index with a query
test_queries = [
    "apartments in Clifton",
    "houses with gardens",
    "properties for rent",
    "modern kitchen",
    "city centre location"
]

print("\nTesting index with sample queries:")
for query in test_queries:
    print(f"\nQuery: '{query}'")
    query_embedding = model.encode([query])
    faiss.normalize_L2(query_embedding)
    
    k = 2  # Number of results to return
    distances, indices = index.search(query_embedding, k)
    
    print(f"Top {k} results:")
    for i in range(k):
        idx = indices[0][i]
        distance = distances[0][i]
        property_id = id_map[str(idx)] if isinstance(id_map, dict) else id_map[idx]
        
        # Find the original listing
        listing = next((l for l in listings if l['id'] == property_id), None)
        if listing:
            print(f"  {i+1}. {listing.get('title', 'Untitled')} (Score: {distance:.4f})")
            print(f"     ID: {property_id}")
            print(f"     {listing.get('description', '')[:100]}...")
        else:
            print(f"  {i+1}. Property ID: {property_id} (Score: {distance:.4f})")

print("\nEmbedding and indexing complete!")
