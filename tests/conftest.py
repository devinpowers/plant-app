import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_environment_and_cosmos_client():
    """
    Mock environment variables and CosmosClient for all tests.
    """
    with patch("os.getenv") as mock_getenv, patch("azure.cosmos.CosmosClient") as mock_client:
        # Mock the environment variable
        mock_getenv.side_effect = lambda key: {
            "COSMOS_DB_CONNECTION_STRING": "AccountEndpoint=https://localhost:8081/;AccountKey=mockkey==;"
        }.get(key, None)

        # Mock CosmosClient
        mock_client_instance = MagicMock()
        mock_client.from_connection_string.return_value = mock_client_instance

        # Mock the database and container clients
        mock_database = mock_client_instance.get_database_client.return_value
        mock_container = mock_database.get_container_client.return_value

        # Mock the container methods
        mock_container.query_items.return_value = [
            {"id": "1", "name": "Mock Plant", "reminder_days": 7, "photo_filename": None}
        ]
        mock_container.upsert_item.return_value = None

        yield mock_container



