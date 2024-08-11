// код виконується після завантаження сторінки
document.addEventListener('DOMContentLoaded', () => {
    // cтворення карти
    const map = L.map('map').setView([50.4501, 30.5234] /* Координати */, 10 /* Масштаб */);
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
        })
        .catch(error => console.error('Error fetching data:', error)); // якщо є помилка, виводимо в консоль

    function updateMap(events) { 
        map.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                map.removeLayer(layer); // Видаляємо всі маркери, щоб не було накладання старих маркерів
            }
        });
        

        events.forEach(event => { // Для кожної події додаємо маркер
            L.marker(event.location)
                .addTo(map)
                //Це вспливаюче вікно, в майбутньому створемо сторінку з повною інформацією
                .bindPopup(`<b>${event.title}</b><br>${event.description}<br><i>Year: ${event.year || event.startYear + '-' + event.endYear}</i>`);
        });
    }

    const startYearRange = document.getElementById('startYear');
    const endYearRange = document.getElementById('endYear');
    const startYearLabel = document.getElementById('startYearLabel');
    const endYearLabel = document.getElementById('endYearLabel');


    // Обробляємо повзунки, якщо значення змінилися, фільтруємо події

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


    // Обробка за пошуком

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


    // Фільтр за пошуком
    function filterEventsBySearchYear(year) {
        const filteredEvents = allEvents.filter(event => event.year == year || 
            (event.startYear && event.endYear && year >= event.startYear && year <= event.endYear));
        updateMap(filteredEvents);
    }

    // Фільтр для повзунків
    function filterEventsByYear(startYear, endYear) {
        const filteredEvents = allEvents.filter(event => 
            (event.year >= startYear && event.year <= endYear) ||
            (event.startYear && event.endYear && endYear >= event.startYear && startYear <= event.endYear)
        );
        updateMap(filteredEvents);
    }

    filterEventsByYear(startYearRange.value, endYearRange.value);
});
