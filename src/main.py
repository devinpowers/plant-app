import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from azure.cosmos import CosmosClient

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'default-key-for-dev')

# Path for file uploads (photos)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Azure Cosmos DB Configuration
DATABASE_NAME = 'plant_database'
CONTAINER_NAME = 'plant_container'


def get_cosmos_container():
    try:
        connection_string = os.getenv("COSMOS_DB_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("COSMOS_DB_CONNECTION_STRING is not set.")

        cosmos_client = CosmosClient.from_connection_string(connection_string)
        database = cosmos_client.get_database_client(DATABASE_NAME)
        container = database.get_container_client(CONTAINER_NAME)
        return container
    except Exception as e:
        print(f"Error connecting to Cosmos DB: {e}")
        raise


@app.route('/')
def index():
    """
    Home page: Lists all plants stored in Cosmos DB.
    """
    try:
        container = get_cosmos_container()
        plants_query = "SELECT * FROM c"
        plants = list(container.query_items(query=plants_query, enable_cross_partition_query=True))

        print("Plants Retrieved:", plants)  # Debugging output
        return render_template('index.html', plants=plants)
    except Exception as e:
        print(f"Error fetching plants: {e}")
        flash("Failed to load plants. Please try again later.", "error")
        return render_template('index.html', plants=[])

@app.route('/add_plant', methods=['GET', 'POST'])
def add_plant():
    """
    Add a new plant. Save the plant to Cosmos DB.
    """
    if request.method == 'POST':
        plant_name = request.form.get('plant_name')
        scientific_name = request.form.get('scientific_name', '')
        personal_name = request.form.get('personal_name', '')
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
            'scientific_name': scientific_name,
            'personal_name': personal_name,
            'reminder_days': reminder_days,
            'photo_filename': photo_filename,
            'health_log': []  # Initialize with an empty list
        }

        # Insert into Cosmos DB
        container = get_cosmos_container()
        container.upsert_item(new_plant)

        flash("Plant added successfully!", "success")
        return redirect(url_for('index'))
    else:
        return render_template('add_plant.html')


@app.route('/plant/<plant_id>')
def view_plant(plant_id):
    """
    View plant details.
    """
    container = get_cosmos_container()
    plant = container.read_item(item=plant_id, partition_key=plant_id)
    return render_template('plant_details.html', plant=plant)



@app.route('/edit_plant/<plant_id>', methods=['GET', 'POST'])
def edit_plant(plant_id):
    container = get_cosmos_container()
    if request.method == 'POST':
        # Retrieve the plant from the database
        plant = container.read_item(item=plant_id, partition_key=plant_id)

        # Update fields
        plant['name'] = request.form.get('plant_name', plant['name'])
        plant['scientific_name'] = request.form.get('scientific_name', plant.get('scientific_name', ''))
        plant['personal_name'] = request.form.get('personal_name', plant.get('personal_name', ''))
        plant['reminder_days'] = int(request.form.get('reminder_days', plant['reminder_days']))

        # Update health log
        new_health_log = request.form.get('health_log', '').strip()
        if new_health_log:
            plant['health_log'] = [{'timestamp': str(datetime.now()), 'note': note.strip()}
                                   for note in new_health_log.split(',')]

        # Save the updated plant back to Cosmos DB
        container.upsert_item(plant)

        flash("Plant updated successfully!", "success")
        return redirect(url_for('view_plant', plant_id=plant_id))
    else:
        # Retrieve the plant and pass it to the template
        try:
            plant = container.read_item(item=plant_id, partition_key=plant_id)
            return render_template('edit_plant.html', plant=plant)
        except Exception as e:
            flash("Plant not found!", "error")
            return redirect(url_for('index'))

@app.route('/delete_plant/<plant_id>', methods=['POST'])
def delete_plant(plant_id):
    """
    Delete a plant.
    """
    container = get_cosmos_container()
    container.delete_item(item=plant_id, partition_key=plant_id)
    flash("Plant deleted successfully.", "success")
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Run on localhost for local testing
    app.run(host='0.0.0.0', port=5001, debug=True)