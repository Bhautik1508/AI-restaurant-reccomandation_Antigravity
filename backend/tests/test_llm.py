import pytest
from unittest.mock import MagicMock, patch
from backend.utils.llm_service import generate_restaurant_analysis

def test_generate_analysis_no_client():
    from backend.utils import llm_service
    # Ensure get_groq_client returns None
    with patch('backend.utils.llm_service.get_groq_client', return_value=None):
        result = generate_restaurant_analysis("Pizza", [])
        assert "Groq API Key missing" in result

def test_generate_analysis_success():
    # Mock the client and response
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "These are great pizza places!"
    mock_client.chat.completions.create.return_value = mock_completion
    
    restaurants = [
        {"name": "Pizza Hut", "cuisine": "Italian", "location": "BTM", "rating": "4.0", "cost": "500"}
    ]
    
    result = generate_restaurant_analysis("Pizza", restaurants, client=mock_client)
    
    assert result == "These are great pizza places!"
    # Verify the prompt construction logic implicitly by checking the call
    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args
    assert "Pizza" in call_args[1]['messages'][0]['content']
    assert "Pizza Hut" in call_args[1]['messages'][0]['content']

def test_generate_analysis_exception():
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    
    result = generate_restaurant_analysis("Pizza", [], client=mock_client)
    assert "Error generating analysis" in result
    assert "API Error" in result
