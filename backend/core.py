import os
import streamlit as st
import pickle
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
from backend.utils.llm_service import generate_restaurant_analysis
from typing import List, Optional

# Load environment variables
load_dotenv()

# Global variables for artifacts
DATA_DIR = "backend/data"
METADATA_PARTS = [
    os.path.join(DATA_DIR, "restaurants_part1.parquet"),
    os.path.join(DATA_DIR, "restaurants_part2.parquet")
]
INDEX_FILE = os.path.join(DATA_DIR, "faiss_index.bin")
MODEL_NAME = "all-MiniLM-L6-v2"

class RecommendationService:
    def __init__(self):
        self.df_restaurants = None
        self.faiss_index = None
        self.embedding_model = None
        self.groq_client = None
        self.loaded = False

    def load_resources(self):
        """Loads all necessary resources for recommendation."""
        if self.loaded:
            return

        # Load Data
        df_parts = []
        for part_path in METADATA_PARTS:
            if os.path.exists(part_path):
                print(f"Loading metadata part from {part_path}...")
                df_parts.append(pd.read_parquet(part_path))
            else:
                print(f"WARNING: Metadata part {part_path} not found.")
        
        if df_parts:
            self.df_restaurants = pd.concat(df_parts)
        else:
            print("ERROR: No metadata parts found.")
            
        # Load Index
        if os.path.exists(INDEX_FILE):
            print(f"Loading FAISS index from {INDEX_FILE}...")
            self.faiss_index = faiss.read_index(INDEX_FILE)
        else:
            print("WARNING: FAISS index not found.")

        # Load Model
        print(f"Loading embedding model {MODEL_NAME}...")
        self.embedding_model = SentenceTransformer(MODEL_NAME)
        
        # Initialize Groq Client
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            self.groq_client = Groq(api_key=api_key)
        else:
            print("WARNING: GROQ_API_KEY not found.")
            
        self.loaded = True

    def get_recommendations(self, query: str, top_k: int = 5):
        """
        Core recommendation logic.
        Returns a dict with 'restaurants' list and 'ai_analysis' string.
        """
        if not self.loaded:
            self.load_resources()
            
        if self.df_restaurants is None or self.faiss_index is None:
            return {"error": "System not initialized. Data missing."}
        
        # 1. Vector Search
        # Fetch more candidates to allow for deduplication
        search_k = top_k * 3
        query_vector = self.embedding_model.encode([query]).astype('float32')
        distances, indices = self.faiss_index.search(query_vector, search_k)
        
        # 2. Retrieve Restaurants
        results = []
        seen_names = set()
        
        for idx in indices[0]:
            if idx < 0 or idx >= len(self.df_restaurants):
                continue
            
            row = self.df_restaurants.iloc[idx]
            
            # Handle potential missing keys safely
            name = row.get('name', 'Unknown')
            
            # Deduplication check
            if name in seen_names:
                continue
            seen_names.add(name)
            
            if len(results) >= top_k:
                break

            cuisine = row.get('cuisines', 'Unknown')
            location = row.get('location', 'Unknown')
            rating = str(row.get('rate', 'N/A'))
            cost = str(row.get('approx_cost(for_two_people)', 'N/A'))
            url = row.get('url', None)
            
            restaurant_data = {
                "name": name,
                "cuisine": cuisine,
                "location": location,
                "rating": rating,
                "cost": cost,
                "url": url
            }
            results.append(restaurant_data)
        
        # 3. LLM Generation
        ai_analysis = generate_restaurant_analysis(query, results, client=self.groq_client)
                
        return {"restaurants": results, "ai_analysis": ai_analysis}

# Singleton instance cached for Streamlit
@st.cache_resource
def get_rec_service():
    service = RecommendationService()
    service.load_resources()
    return service

rec_service = get_rec_service()
