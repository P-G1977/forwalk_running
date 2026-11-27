import { getCurrentMember } from "./auth-api.js";

async function updateNavigation() {
  const signupLink = document.getElementById("nav-signup");
  const loginLink = document.getElementById("nav-login");
  const accountLink = document.getElementById("nav-account");

  if (!signupLink || !loginLink || !accountLink) {
    return;
  }

  try {
    const member = await getCurrentMember();
    const isLoggedIn = member !== null;

    signupLink.hidden = isLoggedIn;
    loginLink.hidden = isLoggedIn;
    accountLink.hidden = !isLoggedIn;
  } catch (error) {
    console.error("Unable to update navigation:", error);
  }
}

updateNavigation();