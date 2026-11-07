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
        cursor.execute("SELECT current_database(), current_user;")

        result = cursor.fetchone()

        print("Connected to database:", result[0])
        print("Connected as user:", result[1])