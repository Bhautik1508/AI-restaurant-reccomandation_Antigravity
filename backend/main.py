import os
import pickle
import faiss
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables
load_dotenv()

app = FastAPI(title="Zomato AI Restaurant Recommender")

# Global variables for artifacts
DATA_DIR = "backend/data"
METADATA_FILE = os.path.join(DATA_DIR, "restaurants.pkl")
INDEX_FILE = os.path.join(DATA_DIR, "faiss_index.bin")
MODEL_NAME = "all-MiniLM-L6-v2"

# In-memory storage
df_restaurants = None
faiss_index = None
embedding_model = None
groq_client = None

class RecommendationRequest(BaseModel):
    query: str
    top_k: int = 5

class Restaurant(BaseModel):
    name: str
    cuisine: str
    location: str
    rating: str
    cost: str
    url: Optional[str] = None

class RecommendationResponse(BaseModel):
    restaurants: List[Restaurant]
    ai_analysis: str

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    global df_restaurants, faiss_index, embedding_model, groq_client
    
    # Load Data
    if os.path.exists(METADATA_FILE):
        print(f"Loading metadata from {METADATA_FILE}...")
        with open(METADATA_FILE, 'rb') as f:
            df_restaurants = pickle.load(f)
    else:
        print("WARNING: Metadata file not found. Please run ingest_data.py first.")
        
    # Load Index
    if os.path.exists(INDEX_FILE):
        print(f"Loading FAISS index from {INDEX_FILE}...")
        faiss_index = faiss.read_index(INDEX_FILE)
    else:
        print("WARNING: FAISS index not found. Please run ingest_data.py first.")

    # Load Model
    print(f"Loading embedding model {MODEL_NAME}...")
    embedding_model = SentenceTransformer(MODEL_NAME)
    
    # Initialize Groq Client
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        groq_client = Groq(api_key=api_key)
    else:
        print("WARNING: GROQ_API_KEY not found in environment variables.")
    
    yield
    # Clean up if needed

app = FastAPI(title="Zomato AI Restaurant Recommender", lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "ok", "data_loaded": df_restaurants is not None}

@app.post("/api/recommend", response_model=RecommendationResponse)
async def recommend(request: RecommendationRequest):
    # Delegate to RecService
    from backend.core import rec_service
    
    result = rec_service.get_recommendations(request.query, request.top_k)
    
    if "error" in result:
        raise HTTPException(status_code=503, detail=result["error"])
        
    # Convert dicts back to Pydantic models
    restaurants = [
        Restaurant(**r) for r in result.get("restaurants", [])
    ]
    
    return RecommendationResponse(restaurants=restaurants, ai_analysis=result.get("ai_analysis", ""))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
