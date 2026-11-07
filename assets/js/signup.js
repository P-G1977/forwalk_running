const signupForm = document.getElementById("signup-form");
const passwordError = document.getElementById("password-error");
const passwordInput = document.getElementById("password");
const confirmPasswordInput = document.getElementById("confirm-password");
const signupMessage = document.getElementById("signup-message");

function validatePasswords() {
  const password = passwordInput.value;
  const confirmPassword = confirmPasswordInput.value;

  if (password !== confirmPassword) {
    passwordError.textContent = "Passwords do not match!";
    passwordError.hidden = false;
    return false;
  }

  passwordError.textContent = "";
  passwordError.hidden = true;

  return true;
}

signupForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!validatePasswords()) {
    return;
  }

  const formData = new FormData(signupForm);

  const registrationData = {
    full_name: formData.get("full_name"),
    email: formData.get("email"),
    password: formData.get("password"),
    confirm_password: formData.get("confirm_password"),
  };

  console.log("Form validation passed!");
  console.log(`Name: ${registrationData.full_name}`);
  console.log(`Email: ${registrationData.email}`);
  try {
    const response = await fetch("http://127.0.0.1:8000/api/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(registrationData),
    });

    const data = await response.json();

    if (response.status === 201) {
      signupMessage.textContent = data.message;
      signupMessage.style.color = "green";

      signupForm.reset();
    } else if (response.status === 409) {
      signupMessage.textContent = data.detail;
      signupMessage.style.color = "red";
    } else {
      signupMessage.textContent =
        "Registration failed. Please check your details.";
      signupMessage.style.color = "red";
    }
  } catch (error) {
    console.error("Network error:", error);
    signupMessage.textContent = "Unable to connect to the server.";
    signupMessage.style.color = "red";
  }
});

passwordInput.addEventListener("input", validatePasswords);
confirmPasswordInput.addEventListener("input", validatePasswords);
