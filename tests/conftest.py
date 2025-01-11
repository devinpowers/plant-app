
import pytest
from unittest.mock import MagicMock

# Import the Flask app and standalone functions
from src.main import app

@pytest.fixture
def client():
    """Fixture to provide a test client for Flask app."""
    app.testing = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_cosmos_container(mocker):
    """Fixture to mock `get_cosmos_container` function in `main.py`."""
    mock_container = MagicMock()
    mocker.patch("src.main.get_cosmos_container", return_value=mock_container)  # Mock `main.get_cosmos_container`
    return mock_container

@pytest.fixture
def mock_blob_service_client(mocker):
    """Fixture to mock `blob_service_client` in `main.py`."""
    mock_blob_client = MagicMock()
    mocker.patch("src.main.blob_service_client", mock_blob_client)  # Mock `main.blob_service_client`
    return mock_blob_client
