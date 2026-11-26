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
  } catch (error) {
    dashboardMessage.textContent =
      "Unable to load your dashboard. Please try again.";

    console.error("Dashboard request failed:", error);
  }
}

loadMemberDashboard();

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
      }
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
  date.textContent = new Date(booking.event_date).toLocaleString(
    "en-GB",
    {
      dateStyle: "full",
      timeStyle: "short",
      timeZone: "Europe/London",
    }
  );

  const location = document.createElement("p");
  location.textContent = `Location: ${booking.location}`;

  card.append(title, description, date, location);

  container.appendChild(card);
});
  } catch (error) {
    console.error("Booking error:", error);
    container.textContent = "Unable to load your bookings.";
  }
}

loadMyBookings();