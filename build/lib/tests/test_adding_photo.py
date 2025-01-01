import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.main import app  # Import the Flask app from your main.py file


class TestPlantApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Set up the Flask app for testing.
        """
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = 'tests/uploads'
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure upload folder exists
        cls.client = app.test_client()

    @classmethod
    def tearDownClass(cls):
        """
        Clean up after tests.
        """
        for file in Path(app.config['UPLOAD_FOLDER']).glob('*'):
            file.unlink()  # Remove test files
        os.rmdir(app.config['UPLOAD_FOLDER'])  # Remove the uploads directory

    @patch('src.main.get_cosmos_container')  # Mock get_cosmos_container
    def test_index_page(self, mock_get_container):
        """
        Test the home page (GET /) for status and content.
        """
        # Mock the database response
        mock_container = MagicMock()
        mock_get_container.return_value = mock_container
        mock_container.query_items.return_value = [
            {"id": "1", "name": "Plant A", "reminder_days": 7},
            {"id": "2", "name": "Plant B", "reminder_days": 14},
        ]

        # Send a GET request to the index route
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Plant A", response.data)  # Check if mock data appears in the response

    @patch('src.main.get_cosmos_container')  # Mock get_cosmos_container
    def test_add_plant(self, mock_get_container):
        """
        Test adding a new plant with a photo.
        """
        # Mock the database container
        mock_container = MagicMock()
        mock_get_container.return_value = mock_container

        # Prepare test data
        plant_name = "Test Plant"
        reminder_days = 7
        test_photo_path = Path(__file__).parent / "test_photo.jpg"

        # Ensure test photo exists
        self.assertTrue(test_photo_path.exists(), "Test photo is missing.")

        # Simulate form data and file upload
        with test_photo_path.open("rb") as photo_file:
            response = self.client.post(
                '/add_plant',
                data={
                    'plant_name': plant_name,
                    'reminder_days': reminder_days,
                    'photo': (photo_file, "test_photo.jpg"),
                },
                content_type="multipart/form-data",
            )

        # Assert that the response redirects to the index page
        self.assertEqual(response.status_code, 302)

        # Assert that the mocked container was used to upsert the item
        mock_container.upsert_item.assert_called_once()
        upserted_item = mock_container.upsert_item.call_args[0][0]
        self.assertEqual(upserted_item['name'], plant_name)
        self.assertEqual(upserted_item['reminder_days'], reminder_days)
        self.assertTrue(upserted_item['photo_filename'], "Photo filename is missing.")

    @patch('src.main.get_cosmos_container')  # Mock get_cosmos_container
    def test_api_plants(self, mock_get_container):
        """
        Test retrieving plants through the API (GET /api/plants).
        """
        # Mock the database response
        mock_container = MagicMock()
        mock_get_container.return_value = mock_container
        mock_container.query_items.return_value = [
            {"id": "1", "name": "Plant A", "reminder_days": 7},
            {"id": "2", "name": "Plant B", "reminder_days": 14},
        ]

        # Send a GET request to the API endpoint
        response = self.client.get('/api/plants')
        self.assertEqual(response.status_code, 200)

        # Assert the response is a list with two items
        json_data = response.get_json()
        self.assertIsInstance(json_data, list)
        self.assertEqual(len(json_data), 2)
        self.assertEqual(json_data[0]['name'], "Plant A")
        self.assertEqual(json_data[1]['name'], "Plant B")


if __name__ == "__main__":
    unittest.main()