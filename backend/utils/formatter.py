def format_ai_analysis(analysis_text):
    """Formats the AI analysis section."""
    if not analysis_text:
        return "No analysis available."
    
    header = "=" * 50 + "\nAI ANALYSIS\n" + "=" * 50 + "\n"
    return f"{header}{analysis_text}\n"

def format_restaurant_card(index, restaurant):
    """Formats a single restaurant card."""
    name = restaurant.get('name', 'Unknown')
    cuisine = restaurant.get('cuisine', 'N/A')
    location = restaurant.get('location', 'N/A')
    rating = restaurant.get('rating', 'N/A')
    cost = restaurant.get('cost', 'N/A')
    url = restaurant.get('url')

    card = [
        f"{index}. {name}",
        f"   Cuisine: {cuisine}",
        f"   Location: {location}",
        f"   Rating: {rating} | Cost: {cost}"
    ]
    
    if url:
        card.append(f"   URL: {url}")
    
    card.append("-" * 30)
    return "\n".join(card)

def format_recommendations_display(data):
    """Generates the full display string for the recommendations."""
    if not data:
        return "No data to display."

    output = []
    
    # AI Analysis
    output.append(format_ai_analysis(data.get("ai_analysis")))
    
    # Restaurants
    header = "=" * 50 + "\nTOP RESTAURANTS\n" + "=" * 50
    output.append(header)
    
    restaurants = data.get("restaurants", [])
    if not restaurants:
        output.append("No restaurants found.")
    else:
        for i, r in enumerate(restaurants, 1):
            output.append(format_restaurant_card(i, r))
            
    return "\n".join(output)
