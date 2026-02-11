import os
from groq import Groq

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return Groq(api_key=api_key)
    return None

def generate_restaurant_analysis(query, restaurants, client=None):
    """
    Generates a recommendation explanation using Groq.
    
    Args:
        query (str): The user's search query.
        restaurants (list): List of Restaurant objects or matching dicts.
        client: Groq client instance. If None, it attempts to create one.
    
    Returns:
        str: The AI analysis text.
    """
    if client is None:
        client = get_groq_client()
        
    if not client:
        return "Analysis unavailable (Groq API Key missing)."

    context_text = ""
    for r in restaurants:
        # Handle both object and dict access for flexibility
        name = getattr(r, 'name', r.get('name', 'Unknown'))
        cuisine = getattr(r, 'cuisine', r.get('cuisine', 'Unknown'))
        location = getattr(r, 'location', r.get('location', 'Unknown'))
        rating = getattr(r, 'rating', r.get('rating', 'N/A'))
        cost = getattr(r, 'cost', r.get('cost', 'N/A'))
        
        context_text += f"- Name: {name}, Cuisine: {cuisine}, Location: {location}, Rating: {rating}, Cost: {cost}\n"

    try:
        prompt = f"""
        You are a helpful food critic and restaurant expert. The user is asking: "{query}"
        
        Here are the top restaurant matches from our database:
        {context_text}
        
        Based on these matches, provide a concise, engaging recommendation explaining why these places fit the user's request. 
        Highlight the best option if clear. Keep it friendly and under 150 words.
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile", 
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error generating analysis: {str(e)}"
