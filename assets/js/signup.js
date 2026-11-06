const signupForm = document.getElementById("signup-form");
const passwordError = document.getElementById("password-error");


signupForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const formData = new FormData(signupForm);
  const name = formData.get("full_name");
  const email = formData.get("email");
  const password = formData.get("password");
  const confirmPassword = formData.get("confirm_password");

  const passwordsMatch = password === confirmPassword;

  if (!passwordsMatch) {
    passwordError.textContent = "Passwords do not match!";
    passwordError.hidden = false;
    return;
  }

  // Clear previous errors when passwords match
  passwordError.textContent = "";
  passwordError.hidden = true;

  console.log("Form validation passed!");

  console.log(`Name: ${name}`);
  console.log(`Email: ${email}`);
});
