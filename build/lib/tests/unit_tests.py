from src.main import app
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    """
    Flask test client fixture.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index(client, mock_environment_and_cosmos_client):
    """
    Test the index route.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"Mock Plant" in response.data


def test_add_plant(client, mock_environment_and_cosmos_client):
    """
    Test the add_plant route.
    """
    response = client.post(
        "/add_plant",
        data={"plant_name": "Spider Plant", "reminder_days": "10"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Plant added successfully!" in response.data

    # Verify the upsert_item method was called
    mock_environment_and_cosmos_client.upsert_item.assert_called_once()
    upserted_item = mock_environment_and_cosmos_client.upsert_item.call_args[0][0]
    assert upserted_item["name"] == "Spider Plant"
    assert upserted_item["reminder_days"] == 10


def test_get_plants_api(client, mock_environment_and_cosmos_client):
    """
    Test the API endpoint for retrieving plants.
    """
    response = client.get("/api/plants")
    assert response.status_code == 200
    assert response.json == [
        {"id": "1", "name": "Mock Plant", "reminder_days": 7, "photo_filename": None}
    ]
