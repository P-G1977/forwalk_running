const signupForm = document.getElementById("signup-form");
const passwordError = document.getElementById("password-error");
const passwordInput = document.getElementById("password");
const confirmPasswordInput = document.getElementById("confirm-password");

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

signupForm.addEventListener("submit", (event) => {
    event.preventDefault();

    // Stop submission if password validation fails
    if (!validatePasswords()) {
        return;
    }

    const formData = new FormData(signupForm);

    const name = formData.get("full_name");
    const email = formData.get("email");

    console.log("Form validation passed!");
    console.log(`Name: ${name}`);
    console.log(`Email: ${email}`);
});

passwordInput.addEventListener("input", validatePasswords);
confirmPasswordInput.addEventListener("input", validatePasswords);