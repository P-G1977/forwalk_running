import os
import psycopg
from psycopg.errors import UniqueViolation
from dotenv import load_dotenv
from argon2 import PasswordHasher
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field
from fastapi.middleware.cors import CORSMiddleware
from argon2.exceptions import VerifyMismatchError, VerificationError
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Response, Cookie, Depends
from typing import Union
import secrets
import hashlib


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


class MemberLogin(BaseModel):
    email: EmailStr
    password: str


def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def generate_session_token():
    token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    return token, token_hash


def create_member_session(member_id):
    token, token_hash = generate_session_token()

    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO public.member_sessions
                    (member_id, token_hash, expires_at)
                VALUES (%s, %s, %s);
                """,
                (member_id, token_hash, expires_at)
            )

    return token


def get_current_member(
    forewalk_session: Union[str, None] = Cookie(default=None)
):
    if forewalk_session is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    token_hash = hashlib.sha256(
        forewalk_session.encode("utf-8")
    ).hexdigest()

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ms.member_id,
                    m.full_name,
                    m.email
                FROM public.member_sessions AS ms
                INNER JOIN public.members AS m
                    ON m.member_id = ms.member_id
                WHERE ms.token_hash = %s
                  AND ms.expires_at > CURRENT_TIMESTAMP
                  AND ms.revoked_at IS NULL;
                """,
                (token_hash,)
            )

            session = cursor.fetchone()

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    return {
        "member_id": session[0],
        "full_name": session[1],
        "email": session[2]
    }


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


@app.post("/api/login")
def login_member(member: MemberLogin, response: Response):
    """Verify a member's login credentials."""

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT member_id, full_name, password_hash
                FROM public.members
                WHERE LOWER(email) = LOWER(%s);
                """,
                (member.email,)
            )

            existing_member = cursor.fetchone()

    if existing_member is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    try:
        password_hasher.verify(
            existing_member[2],
            member.password
        )

    except VerifyMismatchError:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    except VerificationError:
        raise HTTPException(
            status_code=500,
            detail="Unable to verify credentials"
        )

    session_token = create_member_session(existing_member[0])

    response.set_cookie(
        key="forewalk_session",
        value=session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )

    return {
        "message": "Login credentials verified",
        "member_id": existing_member[0],
        "full_name": existing_member[1]
    }

@app.get("/api/me")
def get_my_profile(
    current_member: dict = Depends(get_current_member)
):
    return current_member

@app.post("/api/logout")
def logout_member(
    response: Response,
    forewalk_session: Union[str, None] = Cookie(default=None)
):
    if forewalk_session is not None:
        token_hash = hashlib.sha256(
            forewalk_session.encode("utf-8")
        ).hexdigest()

        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE public.member_sessions
                    SET revoked_at = CURRENT_TIMESTAMP
                    WHERE token_hash = %s
                      AND revoked_at IS NULL;
                    """,
                    (token_hash,)
                )

    response.delete_cookie(
        key="forewalk_session",
        path="/",
        samesite="lax"
    )

    return {
        "message": "Logged out successfully"
    }