import argparse
import requests
import json
import sys

API_URL = "http://localhost:8000/api/recommend"

def get_recommendation(query, top_k=5):
    """Sends a recommendation request to the backend."""
    payload = {
        "query": query,
        "top_k": top_k
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with backend: {e}")
        return None

from backend.utils.formatter import format_recommendations_display

def display_results(data):
    """Formats and prints the recommendation results."""
    print("\n" + format_recommendations_display(data))


def main():
    parser = argparse.ArgumentParser(description="Zomato AI Restaurant Recommender CLI")
    parser.add_argument("query", nargs="?", help="Your restaurant query (e.g., 'Spicy Italian in Bangalore')")
    parser.add_argument("--top_k", type=int, default=5, help="Number of recommendations to retrieve")
    
    args = parser.parse_args()
    
    query = args.query
    if not query:
        print("Welcome to Zomato AI Recommender!")
        print("Let's find you the perfect place to eat.")
        
        cuisine = input("1. What cuisine are you craving? (e.g., North Indian, Italian): ").strip()
        location = input("2. Which location do you prefer? (e.g., Koramangala, Indiranagar): ").strip()
        budget = input("3. What is your budget for two? (e.g., 500, 1000): ").strip()
        
        # Construct a natural language query from the inputs
        parts = []
        if cuisine:
            parts.append(f"{cuisine} food")
        if location:
            parts.append(f"in {location}")
        if budget:
            parts.append(f"budget around {budget}")
            
        if not parts:
            print("No preferences provided. Exiting.")
            return
            
        query = " ".join(parts)
        
    if not query.strip():
        print("Empty query. Exiting.")
        return

    print(f"\nSearching for: '{query}'...")
    result = get_recommendation(query, args.top_k)
    display_results(result)

if __name__ == "__main__":
    main()
