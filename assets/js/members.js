import { cancelBookingRequest } from "./booking-api.js";
const dashboard = document.getElementById("members-dashboard");
const dashboardMessage = document.getElementById("dashboard-message");

async function loadMemberDashboard() {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/me", {
      method: "GET",
      credentials: "include",
    });

    if (response.status === 401) {
      window.location.replace("login.html");
      return;
    }

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const member = await response.json();

    document.getElementById("member-name").textContent = member.full_name;

    document.getElementById("member-email").textContent = member.email;

    dashboard.hidden = false;
    dashboardMessage.hidden = true;

    await loadMyBookings();
  } catch (error) {
    dashboardMessage.textContent =
      "Unable to load your dashboard. Please try again.";

    console.error("Dashboard request failed:", error);
  }
}

const logoutButton = document.getElementById("logout-button");

logoutButton.addEventListener("click", async () => {
  logoutButton.disabled = true;

  try {
    const response = await fetch("http://127.0.0.1:8000/api/logout", {
      method: "POST",
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`Logout failed: ${response.status}`);
    }

    window.location.replace("login.html");
  } catch (error) {
    dashboardMessage.hidden = false;
    dashboardMessage.textContent = "Unable to log out. Please try again.";

    logoutButton.disabled = false;
    console.error("Logout request failed:", error);
  }
});

async function loadMyBookings() {
  const container = document.getElementById("my-bookings-container");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/my-booking-details",
      {
        method: "GET",
        credentials: "include",
      },
    );

    if (!response.ok) {
      throw new Error("Unable to retrieve bookings");
    }

    const bookings = await response.json();

    console.log("My Bookings:", bookings);
    container.replaceChildren();

    if (bookings.length === 0) {
      container.textContent = "You have no upcoming bookings.";
      return;
    }

    bookings.forEach((booking) => {
      const card = document.createElement("article");
      card.classList.add("my-booking-card");

      const title = document.createElement("h3");
      title.textContent = booking.event_name;

      const description = document.createElement("p");
      description.textContent = booking.description;

      const date = document.createElement("p");
      date.textContent = new Date(booking.event_date).toLocaleString("en-GB", {
        dateStyle: "full",
        timeStyle: "short",
        timeZone: "Europe/London",
      });

      const location = document.createElement("p");
      location.textContent = `Location: ${booking.location}`;
      const cancelButton = document.createElement("button");
      cancelButton.type = "button";
      cancelButton.textContent = "Cancel Booking";
      cancelButton.classList.add("book-event-btn", "cancel-booking-btn");

      cancelButton.addEventListener("click", () => {
        cancelMemberBooking(booking.event_id);
      });

      card.append(title, description, date, location, cancelButton);

      container.appendChild(card);
    });
  } catch (error) {
    console.error("Booking error:", error);
    container.textContent = "Unable to load your bookings.";
  }
}

async function cancelMemberBooking(eventId) {
  const confirmed = confirm("Are you sure you want to cancel this booking?");

  if (!confirmed) return;

  try {
    const result = await cancelBookingRequest(eventId);

    alert(result.message);

    await loadMyBookings();
  } catch (error) {
    console.error("Cancellation error:", error);
    alert(error.message || "Unable to cancel booking.");
  }
}

loadMemberDashboard();
