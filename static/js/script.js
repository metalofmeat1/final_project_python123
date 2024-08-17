document.addEventListener('DOMContentLoaded', () => {
    // cтворення карти
    const map = L.map('map').setView([50.4501, 30.5234], 10);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let allEvents = []; // тут всі події, потім ми їх сортуємо

    fetch('/data') // приймаємо події
        .then(response => response.json())
        .then(data => {
            console.log('Data received:', data); // просто перевірка які данні отримали
            allEvents = data.events;   // додаємо до списку
            updateMap(allEvents);
            populateResults(allEvents); // заповнюємо результати по замовчуванню
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
                .bindPopup(`<b>${event.title}</b><br>${event.description}<br><i>Year: ${event.year || event.startYear + '-' + event.endYear}</i>`);
        });
    }

    function populateResults(events) {
        const resultsContainer = document.getElementById('resultsContainer');
        resultsContainer.innerHTML = ''; // Очистити попередні результати
        
        if (events.length === 0) {
            resultsContainer.innerHTML = '<p>No events found for the selected filters.</p>';
            return;
        }
        
        let lastYear = null;
        
        events.forEach(event => {
            if (lastYear !== event.year) {
                if (lastYear !== null) {
                    resultsContainer.innerHTML += '<hr>'; // Розділювач між групами подій
                }
                const yearHeader = document.createElement('h3');
                yearHeader.textContent = `Year: ${event.year || event.startYear + '-' + event.endYear}`;
                resultsContainer.appendChild(yearHeader);
                lastYear = event.year;
            }
            const div = document.createElement('div');
            div.innerHTML = `<b>${event.title}</b><br>${event.description}`;
            resultsContainer.appendChild(div);
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
        const filteredEvents = allEvents.filter(event => event.year == year || 
            (event.startYear && event.endYear && year >= event.startYear && year <= event.endYear));
        updateMap(filteredEvents);
        populateResults(filteredEvents);
    }

    function filterEventsByYear(startYear, endYear) {
        const filteredEvents = allEvents.filter(event => 
            (event.year >= startYear && event.year <= endYear) ||
            (event.startYear && event.endYear && endYear >= event.startYear && startYear <= event.endYear)
        );
        updateMap(filteredEvents);
        populateResults(filteredEvents);
    }

    filterEventsByYear(startYearRange.value, endYearRange.value);

    const toggleSidebar = document.getElementById('toggleSidebar');
    const sidebar = document.getElementById('sidebar');

    toggleSidebar.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
});
