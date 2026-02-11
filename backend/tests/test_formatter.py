import pytest
from backend.utils.formatter import format_ai_analysis, format_restaurant_card, format_recommendations_display

def test_format_ai_analysis():
    text = "This is a test analysis."
    output = format_ai_analysis(text)
    assert "AI ANALYSIS" in output
    assert text in output
    assert "=" * 50 in output

def test_format_restaurant_card():
    restaurant = {
        "name": "Test Resto",
        "cuisine": "Italian",
        "location": "Test Loc",
        "rating": "4.5",
        "cost": "500",
        "url": "http://test.com"
    }
    output = format_restaurant_card(1, restaurant)
    assert "1. Test Resto" in output
    assert "Cuisine: Italian" in output
    assert "URL: http://test.com" in output

def test_format_recommendations_display():
    data = {
        "ai_analysis": "Great!",
        "restaurants": [
            {"name": "R1", "cuisine": "C1", "location": "L1", "rating": "5", "cost": "100"}
        ]
    }
    output = format_recommendations_display(data)
    assert "AI ANALYSIS" in output
    assert "TOP RESTAURANTS" in output
    assert "1. R1" in output
    assert "Great!" in output

def test_format_empty_display():
    output = format_recommendations_display({})
    assert output == "No data to display."
