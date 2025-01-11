import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from azure.cosmos import CosmosClient
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient
# from dotenv import load_dotenv
#
# # Load environment variables from .env file
# load_dotenv()


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


# Initialize Blob Storage client
BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)

container_name = "uploads"
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
    if request.method == 'POST':
        plant_name = request.form.get('plant_name')
        scientific_name = request.form.get('scientific_name', '')
        personal_name = request.form.get('personal_name', '')
        reminder_days_str = request.form.get('reminder_days')
        owner_email = request.form.get('owner_email')
        last_watered_date = request.form.get('last_watered_date')
        reminder_enabled = request.form.get('reminder_enabled') == 'on'

        try:
            reminder_days = int(reminder_days_str)
        except ValueError:
            flash("Please enter a valid number for reminder days.", "error")
            return redirect(url_for('add_plant'))

        plant_id = str(uuid.uuid4())
        photo = request.files.get('photo')
        photo_url = None

        if photo and photo.filename:
            try:
                plant_folder = f"{plant_id}/main.jpg"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=plant_folder)
                blob_client.upload_blob(photo, overwrite=True)
                photo_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{plant_folder}"
            except Exception as e:
                flash(f"Failed to upload photo: {e}", "error")
                return redirect(url_for('add_plant'))

        # Create plant data
        new_plant = {
            'id': plant_id,
            'name': plant_name,
            'scientific_name': scientific_name,
            'reminder_days': reminder_days,
            'reminder_enabled': reminder_enabled,
            'last_watered_date': last_watered_date,
            'owner_email': owner_email,
            'photo_filename': photo_url,
            'health_log': [],
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        try:
            container = get_cosmos_container()
            container.upsert_item(new_plant)
            flash("Plant added successfully!", "success")
        except Exception as e:
            flash(f"Failed to save plant: {e}", "error")
            return redirect(url_for('add_plant'))

        return redirect(url_for('index'))
    return render_template('add_plant.html')



@app.route('/plant/<plant_id>')
def view_plant(plant_id):
    """
    View plant details.
    """
    container = get_cosmos_container()
    plant = container.read_item(item=plant_id, partition_key=plant_id)
    return render_template('plant_details.html', plant=plant)





@app.route('/delete_plant/<plant_id>', methods=['POST'])
def delete_plant(plant_id):
    """
    Delete a plant.
    """
    container = get_cosmos_container()
    container.delete_item(item=plant_id, partition_key=plant_id)
    flash("Plant deleted successfully.", "success")
    return redirect(url_for('index'))

    return render_template('edit_plant.html', plant=plant)


@app.route('/edit_plant/<plant_id>', methods=['GET', 'POST'])
def edit_plant(plant_id):
    container = get_cosmos_container()

    # Fetch the plant data
    try:
        plant = container.read_item(plant_id, partition_key=plant_id)
    except Exception as e:
        flash(f"Error retrieving plant: {e}", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Update plant fields
        plant['name'] = request.form.get('plant_name', plant['name'])
        plant['scientific_name'] = request.form.get('scientific_name', plant['scientific_name'])
        plant['reminder_days'] = int(request.form.get('reminder_days', plant['reminder_days']))
        plant['owner_email'] = request.form.get('owner_email', plant.get('owner_email', ''))
        plant['last_watered_date'] = request.form.get('last_watered_date', plant.get('last_watered_date', ''))
        plant['reminder_enabled'] = request.form.get('reminder_enabled') == 'on'

        # Handle new message and photo
        new_message = request.form.get('message', '').strip()
        photo = request.files.get('photo')
        health_entry = {
            'time': datetime.utcnow().isoformat(),
            'message': new_message if new_message else None,
            'photo': None
        }

        if photo and photo.filename:
            try:
                # Generate a secure filename for the new photo
                filename = secure_filename(f"{plant_id}/Log/{datetime.now().strftime('%Y%m%d_%H%M%S')}_log.jpg")

                # Upload the photo to Azure Blob Storage
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
                blob_client.upload_blob(photo, overwrite=True)

                # Save the photo URL in the health entry
                health_entry['photo'] = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{filename}"
            except Exception as e:
                flash(f"Error uploading photo: {e}", "error")

        # Add the health entry if there's a message or photo
        if health_entry['message'] or health_entry['photo']:
            if 'health_log' not in plant:
                plant['health_log'] = []
            plant['health_log'].append(health_entry)

        # Update the `updated_at` timestamp
        plant['updated_at'] = datetime.utcnow().isoformat()

        # Update the plant in Cosmos DB
        try:
            container.upsert_item(plant)
            flash("Plant updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating plant: {e}", "error")

        return redirect(url_for('view_plant', plant_id=plant_id))

    return render_template('edit_plant.html', plant=plant)

@app.route('/api/plants', methods=['GET'])
def get_plants():
    try:
        container = get_cosmos_container()
        items = list(container.query_items(query="SELECT * FROM c", enable_cross_partition_query=True))
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Attach services to app
app.get_cosmos_container = get_cosmos_container
app.blob_service_client = blob_service_client

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
