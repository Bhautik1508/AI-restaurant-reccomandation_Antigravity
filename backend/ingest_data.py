import os
import pandas as pd
import faiss
import numpy as np
import pickle
from datasets import load_dataset
from sentence_transformers import SentenceTransformer

# Constants
DATASET_NAME = "ManikaSaini/zomato-restaurant-recommendation"
MODEL_NAME = "all-MiniLM-L6-v2"
DATA_DIR = "backend/data"
METADATA_FILE = os.path.join(DATA_DIR, "restaurants.pkl")
INDEX_FILE = os.path.join(DATA_DIR, "faiss_index.bin")

def ingest_data():
    print(f"Loading dataset from {DATASET_NAME}...")
    try:
        dataset = load_dataset(DATASET_NAME, split="train")
        df = dataset.to_pandas()
        print(f"Loaded {len(df)} records.")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # Basic cleaning
    print("Cleaning data...")
    # Inspect columns
    print("Columns:", df.columns.tolist())
    
    # Fill NaN values for critical columns
    # Adjust column names based on actual dataset if needed, assuming standard names for now based on typical Zomato datasets
    # Typical columns: 'name', 'address', 'rate', 'votes', 'phone', 'location', 'rest_type', 'dish_liked', 'cuisines', 'approx_cost(for two people)', 'reviews_list', 'menu_item', 'listed_in(type)', 'listed_in(city)'
    
    # Standardize column names if needed
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    
    text_columns = ['name', 'cuisines', 'location', 'rest_type']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna('')
    
    # Create a combined text field for embedding
    # We want to search by Cuisines, Location, and Name primarily.
    # Reviews could be useful but might be too long/noisy for basic retrieval.
    
    print("Generating embeddings...")
    # Combine fields: "Name: [name]. Cuisine: [cuisine]. Location: [location]. Type: [type]"
    df['combined_text'] = df.apply(
        lambda x: f"Name: {x.get('name', '')}. Cuisine: {x.get('cuisines', '')}. Location: {x.get('location', '')}. Type: {x.get('rest_type', '')}",
        axis=1
    )
    
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(df['combined_text'].tolist(), show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')

    # Create FAISS index
    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Save artifacts
    print(f"Saving data to {DATA_DIR}...")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    # Save metadata (DataFrame)
    with open(METADATA_FILE, 'wb') as f:
        pickle.dump(df, f)
        
    # Save index
    faiss.write_index(index, INDEX_FILE)
    
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest_data()
