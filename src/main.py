import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from azure.cosmos import CosmosClient

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Path for file uploads (photos)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Azure Cosmos DB Configuration
DATABASE_NAME = 'plant_database'
CONTAINER_NAME = 'plant_container'

# Initialize Cosmos DB client and container lazily
import os
from azure.cosmos import CosmosClient

def get_cosmos_container():
    """
    Lazily load the Cosmos DB container.
    """
    connection_string = os.getenv("COSMOS_DB_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("COSMOS_DB_CONNECTION_STRING is not set.")

    # Mocked during tests
    cosmos_client = CosmosClient.from_connection_string(connection_string)
    database = cosmos_client.get_database_client("PlantDatabase")
    return database.get_container_client("PlantsContainer")



@app.route('/')
def index():
    """
    Home page: Lists all plants stored in Cosmos DB.
    """
    container = get_cosmos_container()
    plants_query = "SELECT * FROM c"
    plants = list(container.query_items(query=plants_query, enable_cross_partition_query=True))
    return render_template('index.html', plants=plants)


@app.route('/add_plant', methods=['GET', 'POST'])
def add_plant():
    """
    Add a new plant. Save the plant to Cosmos DB.
    """
    if request.method == 'POST':
        plant_name = request.form.get('plant_name')
        reminder_days_str = request.form.get('reminder_days')

        # Validate reminder_days
        try:
            reminder_days = int(reminder_days_str)
        except ValueError:
            flash("Please enter a valid number for reminder days.", "error")
            return redirect(url_for('add_plant'))

        # Handle optional photo upload
        photo = request.files.get('photo')
        if photo and photo.filename != '':
            photo_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{photo.filename}"
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        else:
            photo_filename = None

        # Create plant entry
        new_plant = {
            'id': str(uuid.uuid4()),  # Generate unique ID for Cosmos DB
            'name': plant_name,
            'reminder_days': reminder_days,
            'photo_filename': photo_filename,
        }

        # Insert into Cosmos DB
        container = get_cosmos_container()
        container.upsert_item(new_plant)

        flash("Plant added successfully!", "success")
        return redirect(url_for('index'))
    else:
        return render_template('add_plant.html')


@app.route('/api/plants', methods=['GET'])
def get_plants_api():
    """
    Example JSON endpoint for retrieving all plants.
    """
    container = get_cosmos_container()
    plants_query = "SELECT * FROM c"
    plants = list(container.query_items(query=plants_query, enable_cross_partition_query=True))
    return jsonify(plants)


if __name__ == '__main__':
    # Run on localhost for local testing
    app.run(host='0.0.0.0', port=5001, debug=True)
