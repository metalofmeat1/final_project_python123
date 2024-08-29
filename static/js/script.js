var map = L.map('map').setView([50.4501, 30.5234], 6);
var allEvents = [];
var markers = [];

// Add the OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
}).addTo(map);

function initMap() {
    fetch('/api/events?year=2024') // Load events for the default year
        .then(response => response.json())
        .then(events => {
            allEvents = events;
            addMarkers(allEvents);
        })
        .catch(error => console.error('Ошибка загрузки подій:', error));
}

function addMarkers(events) {
    // Remove existing markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = []; // Clear markers array

    events.forEach(event => {
        var imageUrl = event.image ? `${event.image}` : '';

        var marker = L.marker([event.latitude, event.longitude]).addTo(map)
            .bindPopup(`
                <b>${event.name}</b><br>
                ${event.description}<br>
                ${event.date}<br>
                ${imageUrl ? `<img src="${imageUrl}" alt="Event Image" style="width: 100px; height: auto;"><br>` : ''}
                <a href="/event/${event.id}">Деталі</a>
            `);

        markers.push(marker);
    });
}

function updateTimelineLabel(year) {
    document.getElementById('timelineLabel').textContent = year;
    document.getElementById('timelineInput').value = year;
    loadEventsForYear(year);
}

function updateTimelineFromInput() {
    var year = document.getElementById('timelineInput').value;
    if (year >= 1000 && year <= 2024) {
        document.getElementById('timeline').value = year;
        updateTimelineLabel(year);
    }
}

function loadEventsForYear(year) {
    fetch(`/api/events?year=${year}`)
        .then(response => response.json())
        .then(events => {
            addMarkers(events);
        });
}

function handleSearchFormSubmit(e) {
    e.preventDefault();
    var query = document.querySelector('#searchForm input[name="query"]').value;

    fetch(`/api/search?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(events => {
            document.getElementById('eventsList').innerHTML = '';

            events.forEach(event => {
                var card = `
                    <div class="col-12 col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">${event.name}</h5>
                                <p class="card-text">${event.date}</p>
                                <a href="/event/${event.id}" class="btn btn-custom">Деталі</a>
                            </div>
                        </div>
                    </div>
                `;

                document.getElementById('eventsList').insertAdjacentHTML('beforeend', card);
            });

            // Add markers for search results
            addMarkers(events);
        })
        .catch(error => console.error('Ошибка поиска:', error));
}

function handleAddEventFormSubmit(e) {
    e.preventDefault();
    var formData = new FormData(document.getElementById('addEventForm'));

    fetch('/api/events', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(event => {
            alert('Подія додана успішно!');
            document.getElementById('addEventForm').reset();
            loadEventsForYear(document.getElementById('timeline').value);
        })
        .catch(error => console.error('Ошибка добавления події:', error));
}

// Event listeners
document.getElementById('searchForm').addEventListener('submit', handleSearchFormSubmit);
document.getElementById('addEventForm').addEventListener('submit', handleAddEventFormSubmit);

// Timeline slider event
document.getElementById('timeline').addEventListener('input', function () {
    updateTimelineLabel(this.value);
});

document.getElementById('timelineInput').addEventListener('change', updateTimelineFromInput);

// Initialize map on page load
document.addEventListener('DOMContentLoaded', function () {
    initMap();
});