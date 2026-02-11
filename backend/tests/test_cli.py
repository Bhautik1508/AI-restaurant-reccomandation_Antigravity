import pytest
import requests
from unittest.mock import patch, MagicMock
from backend.cli_client import get_recommendation, display_results

@patch('backend.cli_client.requests.post')
def test_get_recommendation_success(mock_post):
    """Test successful API call."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    expected_json = {"restaurants": [], "ai_analysis": "Test"}
    mock_response.json.return_value = expected_json
    mock_post.return_value = mock_response
    
    result = get_recommendation("Test query")
    assert result == expected_json
    mock_post.assert_called_once()

@patch('backend.cli_client.requests.post')
def test_get_recommendation_failure(mock_post):
    """Test API failure handling."""
    mock_post.side_effect = requests.exceptions.RequestException("Connection error")
    
    result = get_recommendation("Test query")
    assert result is None

def test_display_results_capsys(capsys):
    """Test output formatting."""
    data = {
        "ai_analysis": "Great choice!",
        "restaurants": [
            {
                "name": "Test Resto",
                "cuisine": "Test Cuisine",
                "location": "Test Loc",
                "rating": "4.5",
                "cost": "500"
            }
        ]
    }
    
    display_results(data)
    captured = capsys.readouterr()
    
    assert "AI ANALYSIS" in captured.out
    assert "Great choice!" in captured.out
    assert "TOP RESTAURANTS" in captured.out
    assert "Test Resto" in captured.out
    assert "Test Cuisine" in captured.out
