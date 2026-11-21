async function loadEvents() {
  const response = await fetch("http://127.0.0.1:8000/api/events");

  if (!response.ok) {
    throw new Error("Failed to load events");
  }

  const events = await response.json();

  const container = document.getElementById("events-container");

container.replaceChildren();

events.forEach((event) => {
  const card = document.createElement("article");
  card.classList.add("event-card");

  const title = document.createElement("h3");
  title.textContent = event.event_name;

  const date = document.createElement("p");
  date.textContent = new Date(event.event_date).toLocaleString("en-GB", {
    dateStyle: "full",
    timeStyle: "short",
    timeZone: "Europe/London",
  });

  const location = document.createElement("p");
  location.textContent = `Location: ${event.location}`;

  const capacity = document.createElement("p");
  capacity.textContent = `${event.available_places} of ${event.max_participants} places available`;

  const description = document.createElement("p");
  description.classList.add("event-description");
  description.textContent = event.description;

  const bookButton = document.createElement("button");
  bookButton.textContent = "Book Event";
  bookButton.classList.add("book-event-btn");
  bookButton.dataset.eventId = event.event_id;

  bookButton.addEventListener("click", () => {
    bookEvent(event.event_id);
});

  card.append(title, description, date, location, capacity, bookButton);
  container.appendChild(card);
});

  console.log(events);
}

loadEvents();

async function bookEvent(eventId) {
    try {
        const response = await fetch(
            `http://127.0.0.1:8000/api/events/${eventId}/book`,
            {
                method: "POST",
                credentials: "include"
            }
        );

        const result = await response.json();

        if (response.status === 401) {
            alert("Please log in before booking an event.");
            return;
        }

        if (!response.ok) {
            alert(result.detail || "Unable to book event.");
            return;
        }

        alert(result.message);

        await loadEvents();

    } catch (error) {
        console.error("Booking error:", error);
        alert("Unable to connect to the booking server.");
    }
}