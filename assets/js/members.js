const dashboard = document.getElementById("members-dashboard");
const dashboardMessage = document.getElementById("dashboard-message");

async function loadMemberDashboard() {
    try {
        const response = await fetch("http://127.0.0.1:8000/api/me", {
            method: "GET",
            credentials: "include"
        });

        if (response.status === 401) {
            window.location.replace("login.html");
            return;
        }

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const member = await response.json();

        document.getElementById("member-name").textContent =
            member.full_name;

        document.getElementById("member-email").textContent =
            member.email;

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
            credentials: "include"
        });

        if (!response.ok) {
            throw new Error(`Logout failed: ${response.status}`);
        }

        window.location.replace("login.html");

    } catch (error) {
        dashboardMessage.hidden = false;
        dashboardMessage.textContent =
            "Unable to log out. Please try again.";

        logoutButton.disabled = false;
        console.error("Logout request failed:", error);
    }
});