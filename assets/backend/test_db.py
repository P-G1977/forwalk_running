import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

with psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
) as connection:

    with connection.cursor() as cursor:
        cursor.execute(
        """
        SELECT member_id, full_name, email
        FROM public.members
        WHERE email = %s;
        """,
        ("test@example.com",)
    )

        member = cursor.fetchone()

        if member:
            print("Member found:", member)
        else:
            print("No member found with that email.")