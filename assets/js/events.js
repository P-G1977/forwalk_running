import { cancelBookingRequest } from "./booking-api.js";

async function loadEvents() {
  const response = await fetch("http://127.0.0.1:8000/api/events");

  if (!response.ok) {
    throw new Error("Failed to load events");
  }

  const events = await response.json();

  const bookedEventIds = await getMyBookings();

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

    if (bookedEventIds.includes(event.event_id)) {
      bookButton.textContent = "Cancel Booking";
      bookButton.classList.add("cancel-booking-btn");

      bookButton.addEventListener("click", () => {
        cancelBooking(event.event_id);
      });
    } else if (event.available_places <= 0) {
      bookButton.textContent = "Fully Booked";
      bookButton.disabled = true;
    } else {
      bookButton.addEventListener("click", () => {
        bookEvent(event.event_id);
      });
    }

    card.append(title, description, date, location, capacity, bookButton);
    container.appendChild(card);
  });

  console.log(events);
}

async function getMyBookings() {
  const response = await fetch("http://127.0.0.1:8000/api/my-bookings", {
    credentials: "include",
  });

  if (response.status === 401) {
    return [];
  }

  if (!response.ok) {
    throw new Error("Unable to load bookings");
  }

  const data = await response.json();

  return data.booked_event_ids;
}

loadEvents().catch((error) => {
  console.error("Failed to load events:", error);
});

async function bookEvent(eventId) {
  try {
    const response = await fetch(
      `http://127.0.0.1:8000/api/events/${eventId}/book`,
      {
        method: "POST",
        credentials: "include",
      },
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

async function cancelBooking(eventId) {
  const confirmed = confirm("Are you sure you want to cancel this booking?");

  if (!confirmed) {
    return;
  }

  try {
    const result = await cancelBookingRequest(eventId);

    alert(result.message);

    await loadEvents();
  } catch (error) {
    console.error("Cancellation error:", error);

    alert(error.message || "Unable to cancel booking.");
  }
}
