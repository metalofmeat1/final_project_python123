var map = L.map('map').setView([50.4501, 30.5234], 6);
var allEvents = [];

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
            allEvents = events;
            events.forEach(event => {
                L.marker([event[4], event[5]]).addTo(map)
                    .bindPopup(`<b>${event[1]}</b><br>${event[2]}<br>${event[3]}`);
            });
        });
}

function handleSearchFormSubmit(e) {
    e.preventDefault();
    var query = document.querySelector('.search-container input[name="query"]').value;

    fetch(`/api/search?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(results => {
            map.eachLayer(function (layer) {
                if (layer instanceof L.Marker) {
                    map.removeLayer(layer);
                }
            });

            results.forEach(result => {
                L.marker([result[4], result[5]]).addTo(map)
                    .bindPopup(`<b>${result[1]}</b><br>${result[2]}<br>${result[3]}`);
            });

            displaySearchResults(results);
        })
        .catch(error => {
            console.error('Ошибка поиска:', error);
        });
}

function displaySearchResults(events) {
    const eventsList = document.getElementById('eventsList');
    eventsList.innerHTML = '';
    events.forEach(event => {
        const eventElement = document.createElement('div');
        eventElement.innerHTML = `
            <h3>${event[1]}</h3>
            <p><strong>Опис:</strong> ${event[2]}</p>
            <p><strong>Дата:</strong> ${event[3]}</p>
            <p><strong>Широта:</strong> ${event[4]}</p>
            <p><strong>Довгота:</strong> ${event[5]}</p>
            <p><strong>Категорія:</strong> ${event[6]}</p>
        `;
        eventsList.appendChild(eventElement);
    });
}

document.getElementById('searchForm').addEventListener('submit', handleSearchFormSubmit);

function toggleTheme() {
    document.body.classList.toggle('dark-theme');
}

map.on('click', function(e) {
    document.getElementById('latitude').value = e.latlng.lat;
    document.getElementById('longitude').value = e.latlng.lng;
});

function addEvent(eventData) {
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
            loadEventsForYear(document.getElementById('timeline').value);
            fetchEvents();
        }
    });
}

document.getElementById('addEventForm').addEventListener('submit', function(e) {
    e.preventDefault();
    var eventData = {
        name: document.getElementById('name').value,
        description: document.getElementById('description').value,
        date: document.getElementById('date').value,
        latitude: parseFloat(document.getElementById('latitude').value),
        longitude: parseFloat(document.getElementById('longitude').value)
    };

    addEvent(eventData);
});

document.addEventListener('DOMContentLoaded', function() {
    loadEventsForYear(document.getElementById('timeline').value);
    fetchEvents();
});

function fetchEvents() {
    fetch('/api/events')
        .then(response => response.json())
        .then(events => {
            const eventsList = document.getElementById('eventsList');
            eventsList.innerHTML = '';
            events.forEach(event => {
                const eventElement = document.createElement('div');
                eventElement.innerHTML = `
                    <h3>${event[1]}</h3>
                    <p><strong>Опис:</strong> ${event[2]}</p>
                    <p><strong>Дата:</strong> ${event[3]}</p>
                    <p><strong>Широта:</strong> ${event[4]}</p>
                    <p><strong>Довгота:</strong> ${event[5]}</p>
                    <p><strong>Категорія:</strong> ${event[6]}</p>
                `;
                eventsList.appendChild(eventElement);
            });
        })
        .catch(error => {
            console.error('Помилка:', error);
        });
}
