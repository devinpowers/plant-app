import pytest
from unittest.mock import patch, MagicMock
from flask import session, get_flashed_messages
from src.main import app  # Adjust the import based on your project structure
from io import BytesIO


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'  # Required for flash messages
    with app.test_client() as client:
        yield client


@patch('src.main.get_cosmos_container')
@patch('src.main.blob_service_client')
def test_add_plant(mock_blob_service_client, mock_get_cosmos_container, client):
    # Mock Cosmos DB container
    mock_container = MagicMock()
    mock_get_cosmos_container.return_value = mock_container

    # Mock Blob Storage client
    mock_blob_client = MagicMock()
    mock_blob_service_client.get_blob_client.return_value = mock_blob_client

    # Simulate form data and file upload
    form_data = {
        'plant_name': 'Monstera',
        'scientific_name': 'Monstera deliciosa',
        'reminder_days': '7',
        'owner_email': 'test@example.com',
        'last_watered_date': '2025-01-10',
        'reminder_enabled': 'on'
    }
    file_data = {
        'photo': (BytesIO(b"fake image content"), 'plant.jpg')
    }

    # Combine form and file data for the POST request
    response = client.post('/add_plant', data={**form_data, **file_data}, content_type='multipart/form-data')

    # Assertions
    assert response.status_code == 302  # Redirect after successful addition
    assert response.headers['Location'] == '/'  # Confirm redirection to index

    # Access flash messages
    with client.session_transaction() as session:
        flash_messages = get_flashed_messages()

    assert "Plant added successfully!" in flash_messages  # Verify the flash message was set
    assert mock_blob_service_client.get_blob_client.called
    assert mock_blob_client.upload_blob.called
    assert mock_container.upsert_item.called