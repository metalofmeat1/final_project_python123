var map = L.map('map').setView([50.4501, 30.5234], 6);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
}).addTo(map);

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
            map.eachLayer(function (layer) {
                if (layer instanceof L.Marker) {
                    map.removeLayer(layer);
                }
            });
            events.forEach(event => {
                L.marker([event[4], event[5]]).addTo(map)
                    .bindPopup(`<b>${event[1]}</b><br>${event[2]}<br>${event[3]}`);
            });
        });
}

map.on('click', function(e) {
    document.getElementById('latitude').value = e.latlng.lat;
    document.getElementById('longitude').value = e.latlng.lng;
});

document.getElementById('addEventForm').addEventListener('submit', function(e) {
    e.preventDefault();
    var eventData = {
        name: document.getElementById('name').value,
        description: document.getElementById('description').value,
        date: document.getElementById('date').value,
        latitude: parseFloat(document.getElementById('latitude').value),
        longitude: parseFloat(document.getElementById('longitude').value)
    };

    fetch('/api/add_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(eventData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            L.marker([eventData.latitude, eventData.longitude]).addTo(map)
                .bindPopup(`<b>${eventData.name}</b><br>${eventData.description}<br>${eventData.date}`);
        }
    });
});

loadEventsForYear(document.getElementById('timeline').value);
