from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

password_hasher = PasswordHasher()

password = "Adifferentpassword123!"

# Generate a secure hash
hashed_password = password_hasher.hash(password)

print("Hashed password:", hashed_password)

# Verify the correct password
is_valid = password_hasher.verify(hashed_password, password)

print("Correct password:", is_valid)

# Test an incorrect password
try:
    password_hasher.verify(hashed_password, "WrongPassword123!")
except VerifyMismatchError:
    print("Incorrect password rejected!")