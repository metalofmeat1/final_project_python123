document.addEventListener("DOMContentLoaded", () => {
  const map = L.map("map").setView([50.4501, 30.5234], 10);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  let allEvents = [];

  function fetchEvents(period = null, search = null) {
    let url = "/api/data";
    if (period || search) {
      url += "?";
      if (period) url += `period=${period}`;
      if (search) url += `&search=${search}`;
    }

    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        console.log("Data received:", data);
        allEvents = data.events;
        updateMap(allEvents);
        updateSidebar(allEvents);
      })
      .catch((error) => console.error("Error fetching data:", error));
  }

  fetchEvents();

  function updateMap(events) {
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        map.removeLayer(layer);
      }
    });

    events.forEach((event) => {
      if (event.location && event.location.length === 2) {
        L.marker(event.location).addTo(map).bindPopup(`
          <b>${event.title}</b><br>
          ${event.description}<br>
          <i>Year: ${event.year || (event.startYear && event.endYear ? event.startYear + '-' + event.endYear : 'Unknown')}</i><br>
        `);
      } else {
        console.error("Invalid location data for event:", event);
      }
    });
  }

  function updateSidebar(events) {
    const resultsContainer = document.getElementById("resultsContainer");
    resultsContainer.innerHTML = "";

    events.forEach((event) => {
      const eventElement = document.createElement("div");
      eventElement.className = "event-item";

      eventElement.innerHTML = `
        <h3>${event.title}</h3>
        <p>${event.description}</p>
        <p><i>Year: ${event.year || (event.startYear && event.endYear ? event.startYear + '-' + event.endYear : 'Unknown')}</i></p>
        <hr style="margin: 10px 0; border: 1px solid #ccc;"/>
      `;

      resultsContainer.appendChild(eventElement);
    });
  }

  const yearRange = document.getElementById("yearRange");
  const startYearLabel = document.getElementById("startYearLabel");
  const endYearLabel = document.getElementById("endYearLabel");

  noUiSlider.create(yearRange, {
    start: [1000, 2024],
    connect: true,
    range: {
      'min': 1000,
      'max': 2024
    },
    step: 1
  });

  yearRange.noUiSlider.on("update", (values) => {
    const startYear = Math.round(values[0]);
    const endYear = Math.round(values[1]);

    startYearLabel.textContent = startYear;
    endYearLabel.textContent = endYear;
    filterEventsByYear(startYear, endYear);
  });

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
    updateSidebar(filteredEvents);
  }

  filterEventsByYear(1000, 2024);

  const sidebar = document.getElementById("sidebar");
  const toggleSidebar = document.getElementById("toggleSidebar");

  toggleSidebar.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });

  document.getElementById("searchButton").addEventListener("click", () => {
    const searchYear = parseInt(document.getElementById("searchYear").value);

    if (!isNaN(searchYear) && searchYear >= 1000 && searchYear <= 2024) {
      yearRange.noUiSlider.set([searchYear, searchYear]);
    } else {
      alert("Please enter a valid year between 1000 and 2024.");
    }

    document.getElementById("searchYear").value = '';
  });

  const periodSelect = document.getElementById("periodSelect");
  periodSelect.addEventListener("change", () => {
    fetchEvents(periodSelect.value);
  });

  const searchInput = document.getElementById("searchInput");
  searchInput.addEventListener("input", () => {
    fetchEvents(null, searchInput.value);
  });
});
