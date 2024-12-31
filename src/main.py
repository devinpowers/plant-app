import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # for session/flash usage

# Path for file uploads (photos)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory plant "database"
PLANTS_DB = []  # This will reset every time the app restarts

@app.route('/')
def index():
    """
    Home page: Lists all plants in our in-memory store.
    We also have a little bit of JavaScript to make it look nicer.
    """
    return render_template('index.html', plants=PLANTS_DB)

@app.route('/add_plant', methods=['GET', 'POST'])
def add_plant():
    """
    Add a new plant. 'reminder_days' is now an integer for how many days.
    """
    if request.method == 'POST':
        plant_name = request.form.get('plant_name')
        # Convert the water schedule to an integer
        reminder_days_str = request.form.get('reminder_days')
        try:
            reminder_days = int(reminder_days_str)
        except ValueError:
            flash("Please enter a valid number for reminder days.", "error")
            return redirect(url_for('add_plant'))

        # Handle optional photo upload
        photo = request.files.get('photo')
        if photo and photo.filename != '':
            # Use a timestamp to avoid filename collisions
            photo_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{photo.filename}"
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        else:
            photo_filename = None

        # Create plant entry
        plant_id = len(PLANTS_DB) + 1
        new_plant = {
            'id': plant_id,
            'name': plant_name,
            'reminder_days': reminder_days,  # integer
            'photo_filename': photo_filename,
        }

        # Append to our in-memory list
        PLANTS_DB.append(new_plant)

        flash("Plant added successfully!", "success")
        return redirect(url_for('index'))
    else:
        return render_template('add_plant.html')

@app.route('/api/plants', methods=['GET'])
def get_plants_api():
    """
    Example JSON endpoint for retrieving all plants.
    """
    return jsonify(PLANTS_DB)

if __name__ == '__main__':
    # Run on localhost:5000
    app.run(debug=True)

