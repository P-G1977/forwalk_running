import os

import psycopg
from dotenv import load_dotenv
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

load_dotenv()

password_hasher = PasswordHasher()

test_email = "test@example.com"
test_password = "ForewalkTest123!"

# Connect to PostgreSQL
with psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
) as connection:

    with connection.cursor() as cursor:

        # Step 2: Execute our parameterised SELECT
        cursor.execute(
            """
            SELECT member_id, full_name, password_hash
            FROM public.members
            WHERE LOWER(email) = LOWER(%s);
            """,
            (test_email,)
        )

        # Step 3: Retrieve the result
        member = cursor.fetchone()

        if member:
            try:
                password_hasher.verify(member[2], test_password)

                print("Login successful!")
                print("Welcome:", member[1])

            except VerifyMismatchError:
                print("Invalid email or password.")

            except VerificationError:
                print("Password verification failed.")

        else:
            print("Invalid email or password.")