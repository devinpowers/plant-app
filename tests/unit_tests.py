import pytest
from src.main import app

@pytest.fixture
def client():
    # Create a test client for our Flask app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"My Plants" in response.data

def test_add_plant_get(client):
    response = client.get('/add_plant')
    assert response.status_code == 200
    assert b"Add a New Plant" in response.data

def test_add_plant_post(client):
    # Mock form data
    data = {
        'plant_name': 'Test Plant',
        'watering_schedule': 'Every 3 days'
        # 'photo' can be tested with file uploads as well
    }
    response = client.post('/add_plant', data=data, follow_redirects=True)
    assert response.status_code == 200
    # Check if plant was added
    assert b"Plant added successfully!" in response.data
