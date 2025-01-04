function showPlantDetails(plantId) {
    fetch(`/api/plants/${plantId}`)
        .then(response => response.json())
        .then(plant => {
            document.getElementById('plant-name').innerText = plant.name;
            document.getElementById('scientific-name').innerText = `Scientific Name: ${plant.scientific_name}`;
            document.getElementById('care-instructions').innerText = `Care Instructions: Water every ${plant.reminder_days} day(s)`;

            const healthLog = document.getElementById('health-log');
            healthLog.innerHTML = plant.health_log.map(log => `<li>${log}</li>`).join('');

            document.getElementById('plant-modal').style.display = 'block';
        });
}

function addHealthNote() {
    const plantId = document.getElementById('plant-name').dataset.id;
    const note = document.getElementById('health-note').value;

    if (note) {
        fetch(`/api/plants/${plantId}/health`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ note })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            showPlantDetails(plantId);
        });
    }
}

function filterPlants() {
    const query = document.getElementById('search-bar').value;

    fetch(`/api/plants/search?query=${query}`)
        .then(response => response.json())
        .then(plants => {
            const gallery = document.getElementById('plant-gallery');
            gallery.innerHTML = '';
            plants.forEach(plant => {
                const plantCard = `
                    <div class="plant-card" onclick="showPlantDetails('${plant.id}')">
                        <img src="/static/uploads/${plant.photo_filename}" alt="${plant.name}">
                        <h3>${plant.name}</h3>
                        <p>Reminder every ${plant.reminder_days} day(s)</p>
                    </div>
                `;
                gallery.innerHTML += plantCard;
            });
        });
}

function closeModal() {
    document.getElementById('plant-modal').style.display = 'none';
}

function showPlantDetails(plantId) {
    fetch(`/api/plants/${plantId}`)
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById("modal");
            const modalContent = modal.querySelector(".modal-content");
            modalContent.innerHTML = `
                <span class="close" onclick="closeModal()">&times;</span>
                <h2>${data.name}</h2>
                <p><strong>Scientific Name:</strong> ${data.scientific_name || "N/A"}</p>
                <p><strong>Personal Name:</strong> ${data.personal_name || "N/A"}</p>
                <p><strong>Reminder:</strong> Every ${data.reminder_days} day(s)</p>
                <p><strong>Health Log:</strong> ${data.health_log || "No health logs yet."}</p>
            `;
            modal.style.display = "flex";
        })
        .catch(error => {
            console.error("Error fetching plant details:", error);
        });
}

function closeModal() {
    const modal = document.getElementById("modal");
    modal.style.display = "none";
}
