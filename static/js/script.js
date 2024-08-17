document.addEventListener("DOMContentLoaded", () => {
  // створення карти
  const map = L.map("map").setView([50.4501, 30.5234], 10); // Координати і масштаб
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  let allEvents = []; // тут всі події, потім ми їх сортуємо

  fetch("/data") // приймаємо події
    .then((response) => response.json())
    .then((data) => {
      console.log("Data received:", data); // просто перевірка які данні отримали
      allEvents = data.events; // додаємо до списку
      updateMap(allEvents);
      updateSidebar(allEvents);
    })
    .catch((error) => console.error("Error fetching data:", error)); // якщо є помилка, виводимо в консоль

  function updateMap(events) {
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        map.removeLayer(layer); // видаляємо всі маркери
      }
    });

    events.forEach((event) => {
      // додаємо маркер
      L.marker(event.location).addTo(map).bindPopup(`
        <b>${event.title}</b><br>
        ${event.description}<br>
        <i>Year: ${event.year || (event.startYear && event.endYear ? event.startYear + '-' + event.endYear : 'Unknown')}</i><br>
      `);
    });
  }

  function updateSidebar(events) {
    const resultsContainer = document.getElementById("resultsContainer");
    resultsContainer.innerHTML = ""; // очищуємо результати

    events.forEach((event) => {
      const eventElement = document.createElement("div");
      eventElement.className = "event-item"; // клас для стилізації

      eventElement.innerHTML = `
        <h3>${event.title}</h3>
        <p>${event.description}</p>
        <p><i>Year: ${event.year || (event.startYear && event.endYear ? event.startYear + '-' + event.endYear : 'Unknown')}</i></p>
        <hr style="margin: 10px 0; border: 1px solid #ccc;"/>
      `;

      resultsContainer.appendChild(eventElement);
    });
  }

  const startYearRange = document.getElementById("startYear");
  const endYearRange = document.getElementById("endYear");
  const startYearLabel = document.getElementById("startYearLabel");
  const endYearLabel = document.getElementById("endYearLabel");

  // якщо значення шкад змінилося, ми фільтруємо події
  startYearRange.addEventListener("input", () => {
    const startYear = parseInt(startYearRange.value);
    startYearLabel.textContent = startYear;
    filterEventsByYear(startYear, parseInt(endYearRange.value));
  });

  endYearRange.addEventListener("input", () => {
    const endYear = parseInt(endYearRange.value);
    endYearLabel.textContent = endYear;
    filterEventsByYear(parseInt(startYearRange.value), endYear);
  });

  // обробка за пошуком дати
  const searchYearInput = document.getElementById("searchYear");
  const searchButton = document.getElementById("searchButton");

  searchButton.addEventListener("click", () => {
    const searchYear = parseInt(searchYearInput.value);
    startYearRange.value = startYearRange.min;
    endYearRange.value = endYearRange.max;
    startYearLabel.textContent = startYearRange.value;
    endYearLabel.textContent = endYearRange.value;
    filterEventsBySearchYear(searchYear);
  });

  // фільтр за пошуком
  function filterEventsBySearchYear(year) {
    const filteredEvents = allEvents.filter(
      (event) =>
        (event.year && parseInt(event.year) === year) ||
        (event.startYear && event.endYear &&
          year >= parseInt(event.startYear) &&
          year <= parseInt(event.endYear))
    );
    updateMap(filteredEvents);
    updateSidebar(filteredEvents); //  оновлення сайд-бара
  }

  // фільтр для повзунків
  function filterEventsByYear(startYear, endYear) {
    const filteredEvents = allEvents.filter((event) => {
      const eventStartYear = event.startYear ? parseInt(event.startYear) : null;
      const eventEndYear = event.endYear ? parseInt(event.endYear) : null;
      const eventYear = event.year ? parseInt(event.year) : null;

      return (
        (eventYear && eventYear >= startYear && eventYear <= endYear) ||
        (eventStartYear && eventEndYear && startYear <= eventEndYear && endYear >= eventStartYear)
      );
    });
    updateMap(filteredEvents);
    updateSidebar(filteredEvents); //  оновлення сайд-бара
  }

  // фільтрації за початковими значеннями
  filterEventsByYear(parseInt(startYearRange.value), parseInt(endYearRange.value));

  const sidebar = document.getElementById("sidebar");
  const toggleSidebar = document.getElementById("toggleSidebar");

  toggleSidebar.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });
});
