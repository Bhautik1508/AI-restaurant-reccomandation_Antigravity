import streamlit as st
import os
from backend.core import rec_service

st.set_page_config(
    page_title="Zomato AI Recommender",
    page_icon="🍽️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .restaurant-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    .restaurant-name {
        font-size: 1.25rem;
        font-weight: bold;
        color: #ff4b4b;
        margin-bottom: 5px;
    }
    .metric-row {
        display: flex;
        gap: 15px;
        color: #ccc;
        font-size: 0.9rem;
    }
    .ai-analysis {
        background-color: #2b1c1c;
        border-left: 5px solid #ff4b4b;
        padding: 15px;
        margin-bottom: 25px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🍽️ Zomato AI Restaurant Recommender")
st.markdown("Discover the best places to eat in Bengaluru using AI-powered search.")

# Sidebar Inputs
with st.sidebar:
    st.header("Your Preferences")
    
    cuisine = st.text_input("Cuisine", placeholder="e.g., North Indian, Italian, Sushi")
    location = st.text_input("Location", placeholder="e.g., Koramangala, Indiranagar")
    top_k = st.slider("Number of Recommendations", 3, 10, 5)
    
    st.markdown("---")
    search_btn = st.button("Find Restaurants", type="primary", use_container_width=True)

# Initialize session state for persistent results
if "results" not in st.session_state:
    st.session_state["results"] = None

# Main Content
if search_btn:
    if not cuisine and not location:
        st.warning("Please enter at least a cuisine or a location.")
    else:
        # Construct Query
        parts = []
        if cuisine: parts.append(f"{cuisine} food")
        if location: parts.append(f"in {location}")
        query = " ".join(parts)
        
        with st.spinner(f"Searching for '{query}'..."):
            try:
                # Direct Backend Call (No HTTP Request)
                data = rec_service.get_recommendations(query, top_k)
                
                if "error" in data:
                    st.error(f"Error: {data['error']}")
                else:
                    # Store in session state for persistence
                    st.session_state["results"] = data
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Display results from session state
if st.session_state["results"]:
    data = st.session_state["results"]
    
    # AI Analysis Section
    if "ai_analysis" in data:
        st.subheader("🤖 AI Analysis")
        st.markdown(f"""
        <div class="ai-analysis">
            {data['ai_analysis']}
        </div>
        """, unsafe_allow_html=True)
    
    # Restaurant Cards
    st.subheader("Top Recommendations")
    restaurants = data.get("restaurants", [])
    
    if not restaurants:
        st.info("No restaurants found matching your criteria.")
    
    for i, r in enumerate(restaurants, 1):
        name = r.get('name', 'Unknown')
        r_cuisine = r.get('cuisine', 'N/A')
        r_loc = r.get('location', 'N/A')
        rating = r.get('rating', 'N/A')
        cost = r.get('cost', 'N/A')
        url = r.get('url')
        
        # Render Card
        with st.container():
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"### {i}. {name}")
                st.markdown(f"**Cuisine:** {r_cuisine} | **Location:** {r_loc}")
                st.markdown(f"**Rating:** {rating}/5 ⭐ | **Cost:** ₹{cost} for two")
            with cols[1]:
                if url:
                    st.markdown(f"[**View on Zomato**]({url})")
                else:
                    st.write("No Link")
            st.markdown("---")

else:
    # Landing State
    st.info("👈 Enter your preferences in the sidebar to get started!")
