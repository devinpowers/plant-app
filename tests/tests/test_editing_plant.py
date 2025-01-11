import pytest
from unittest.mock import patch, MagicMock
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
def test_edit_plant(mock_blob_service_client, mock_get_cosmos_container, client):
    # Mock Cosmos DB container
    mock_container = MagicMock()
    mock_get_cosmos_container.return_value = mock_container

    # Mock Blob Storage client
    mock_blob_client = MagicMock()
    mock_blob_service_client.get_blob_client.return_value = mock_blob_client

    # Mock plant data in the database
    plant_id = "12345"
    mock_plant_data = {
        'id': plant_id,
        'name': 'Monstera',
        'scientific_name': 'Monstera deliciosa',
        'reminder_days': 7,
        'owner_email': 'test@example.com',
        'last_watered_date': '2025-01-10',
        'reminder_enabled': True,
        'health_log': [],
        'updated_at': '2025-01-10T12:00:00Z',
    }
    mock_container.read_item.return_value = mock_plant_data

    # Simulate form data and file upload
    form_data = {
        'plant_name': 'New Monstera',
        'scientific_name': 'Monstera deliciosa var. borsigiana',
        'reminder_days': '10',
        'owner_email': 'new_email@example.com',
        'last_watered_date': '2025-01-11',
        'reminder_enabled': 'on',
        'message': 'Looking healthy!',
    }
    file_data = {
        'photo': (BytesIO(b"fake image content"), 'new_photo.jpg')
    }

    # Combine form and file data for the POST request
    response = client.post(f'/edit_plant/{plant_id}', data={**form_data, **file_data}, content_type='multipart/form-data')

    # Assertions
    assert response.status_code == 302  # Redirect after successful edit
    assert response.headers['Location'] == f'/plant/{plant_id}'  # Redirect to the correct detail page

    # Verify Cosmos DB interactions
    mock_container.read_item.assert_called_once_with(plant_id, partition_key=plant_id)
    assert mock_container.upsert_item.called

    # Verify Blob Storage interactions
    assert mock_blob_service_client.get_blob_client.called
    assert mock_blob_client.upload_blob.called

    # Verify the plant data was updated correctly
    updated_plant = mock_container.upsert_item.call_args[0][0]
    assert updated_plant['name'] == 'New Monstera'
    assert updated_plant['scientific_name'] == 'Monstera deliciosa var. borsigiana'
    assert updated_plant['reminder_days'] == 10
    assert updated_plant['owner_email'] == 'new_email@example.com'
    assert updated_plant['last_watered_date'] == '2025-01-11'
    assert updated_plant['reminder_enabled'] is True
    assert 'health_log' in updated_plant
    assert len(updated_plant['health_log']) == 1
    assert updated_plant['health_log'][0]['message'] == 'Looking healthy!'
