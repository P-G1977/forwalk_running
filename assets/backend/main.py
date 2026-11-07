import os

import psycopg
from psycopg.errors import UniqueViolation
from dotenv import load_dotenv
from argon2 import PasswordHasher
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Forewalk Games API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8001"
    ],
    allow_methods=["POST"],
    allow_headers=["Content-Type"]
)

load_dotenv()

password_hasher = PasswordHasher()

class MemberRegistration(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=12)
    confirm_password: str

def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

@app.get("/api/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {
        "status": "ok",
        "application": "Forewalk Games"
    }


@app.post("/api/register", status_code=201)
def register_member(member: MemberRegistration):
    """Register a new member in PostgreSQL."""

    # 1. Validate matching passwords
    if member.password != member.confirm_password:
        raise HTTPException(
            status_code=422,
            detail="Passwords do not match"
        )

    # 2. Hash the password
    hashed_password = password_hasher.hash(member.password)

    # 3. Insert the member into PostgreSQL
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO public.members (
                        full_name,
                        email,
                        password_hash
                    )
                    VALUES (%s, %s, %s)
                    RETURNING member_id;
                    """,
                    (
                        member.full_name,
                        member.email,
                        hashed_password
                    )
                )

                member_id = cursor.fetchone()[0]

    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists"
        )

    # 4. Return a safe response
    return {
        "message": "Member registered successfully",
        "member_id": member_id
    }
