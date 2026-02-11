import pytest
import subprocess
import time
import requests
import os

@pytest.fixture(scope="module")
def streamlit_app():
    """Fixtures that starts the Streamlit app and tears it down."""
    # Start streamlit in the background
    # Note: We assume uvicorn is already running or we test the frontend isolation mostly
    # But for a true integration we need both. 
    # For this test, verifying the Streamlit server starts and serves content is sufficient.
    
    cmd = ["streamlit", "run", "frontend_app.py", "--server.port=8502", "--server.headless=true"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for it to start
    time.sleep(5)
    
    yield "http://localhost:8502"
    
    # Teardown
    process.terminate()
    process.wait()

def test_streamlit_app_is_reachable(streamlit_app):
    """Verifies that the Streamlit app is up and running."""
    try:
        response = requests.get(streamlit_app, timeout=10)
        assert response.status_code == 200
        # Streamlit serves a React app shell, so we just check for basic title/content
        # validation might be limited without a full browser driver like Selenium/Playwright
        # but status 200 confirms the server is running.
    except requests.exceptions.ConnectionError:
        pytest.fail("Streamlit app is not reachable.")
