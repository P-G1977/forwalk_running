import { API_BASE_URL } from "./config.js";
import { getCurrentMember } from "./auth-api.js";
const loginForm = document.getElementById("login-form");
const loginMessage = document.getElementById("login-message");

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(loginForm);

  const loginData = {
    email: formData.get("email"),
    password: formData.get("password"),
  };

  try {
    const response = await fetch(`${API_BASE_URL}/api/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify(loginData),
    });

    const data = await response.json();

    if (response.ok) {
      loginMessage.textContent = `Welcome back, ${data.full_name}!`;
      loginMessage.style.color = "green";

      window.location.replace("members.html");
    } else {
      loginMessage.textContent = data.detail || "Login failed.";
      loginMessage.style.color = "red";
    }
  } catch (error) {
    loginMessage.textContent = "Unable to connect to the server.";
    loginMessage.style.color = "red";
    console.error("Login request failed:", error);
  }
});

async function checkLoginStatus() {
  try {
    const member = await getCurrentMember();

    if (!member) {
      console.log("No active login session.");
      return;
    }

    console.log("Logged in member ID:", member.member_id);
    console.log("Logged in member name:", member.full_name);
  } catch (error) {
    console.error("Unable to check login status:", error);
  }
}

checkLoginStatus();
