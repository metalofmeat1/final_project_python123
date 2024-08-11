document.addEventListener('DOMContentLoaded', () => {
    const map = L.map('map').setView([50.4501, 30.5234], 10);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let allEvents = []; 

    fetch('/data')
        .then(response => response.json())
        .then(data => {
            console.log('Data received:', data); 
            allEvents = data.events;  
            updateMap(allEvents); 
        })
        .catch(error => console.error('Error fetching data:', error));

    function updateMap(events) {
        map.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                map.removeLayer(layer); 
            }
        });

        events.forEach(event => {
            L.marker(event.location)
                .addTo(map)
                .bindPopup(`<b>${event.title}</b><br>${event.description}<br><i>Year: ${event.year}</i>`);
        });
    }

    const startYearRange = document.getElementById('startYear');
    const endYearRange = document.getElementById('endYear');
    const startYearLabel = document.getElementById('startYearLabel');
    const endYearLabel = document.getElementById('endYearLabel');

    startYearRange.addEventListener('input', () => {
        const startYear = startYearRange.value;
        startYearLabel.textContent = startYear;
        filterEventsByYear(startYear, endYearRange.value);
    });

    endYearRange.addEventListener('input', () => {
        const endYear = endYearRange.value;
        endYearLabel.textContent = endYear;
        filterEventsByYear(startYearRange.value, endYear);
    });

    const searchYearInput = document.getElementById('searchYear');
    const searchButton = document.getElementById('searchButton');

    searchButton.addEventListener('click', () => {
        const searchYear = searchYearInput.value;
        startYearRange.value = startYearRange.min;
        endYearRange.value = endYearRange.max;
        startYearLabel.textContent = startYearRange.value;
        endYearLabel.textContent = endYearRange.value;
        filterEventsBySearchYear(searchYear);
    });

    function filterEventsBySearchYear(year) {
        const filteredEvents = allEvents.filter(event => event.year == year);
        updateMap(filteredEvents);
    }

    function filterEventsByYear(startYear, endYear) {
        const filteredEvents = allEvents.filter(event => event.year >= startYear && event.year <= endYear);
        updateMap(filteredEvents);
    }

    filterEventsByYear(startYearRange.value, endYearRange.value);
});
