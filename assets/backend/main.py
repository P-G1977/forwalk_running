import os
from pathlib import Path
import psycopg
from psycopg.errors import UniqueViolation
from dotenv import load_dotenv
from argon2 import PasswordHasher
from fastapi import FastAPI, HTTPException, Response, Cookie, Depends, Request
from pydantic import BaseModel, EmailStr, Field
from fastapi.middleware.cors import CORSMiddleware
from argon2.exceptions import VerifyMismatchError, VerificationError
from datetime import datetime, timedelta, timezone
from typing import Union
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import secrets
import hashlib


app = FastAPI(title="Forewalk Games API")

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"]
)

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

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

def record_login_attempt(email, ip_address, successful):
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO public.login_attempts
                    (email, ip_address, successful)
                VALUES (%s, %s, %s);
            """, (email, ip_address, successful))

def count_failed_login_attempts(email, ip_address):
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*)
                FROM public.login_attempts
                WHERE LOWER(email) = LOWER(%s)
                  AND ip_address IS NOT DISTINCT FROM %s
                  AND successful = FALSE
                  AND attempted_at >= CURRENT_TIMESTAMP - INTERVAL '15 minutes';
            """, (email, ip_address))

            failed_attempts = cursor.fetchone()[0]

    return failed_attempts


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
@limiter.limit("5/15minutes")
def login_member(
    request: Request,
    member: MemberLogin,
    response: Response
):
    ip_address = request.client.host if request.client else None
    failed_count = count_failed_login_attempts(
        member.email,
        ip_address
    )
    if failed_count >= 5:
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again later."
        )


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
        record_login_attempt(
            member.email,
            request.client.host if request.client else None,
            False
    )

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
        record_login_attempt(
            member.email,
            request.client.host if request.client else None,
            False
    )

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

@app.get("/api/events")
def get_events():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
    SELECT
        e.event_id,
        e.event_name,
        e.description,
        e.event_date,
        e.location,
        e.max_participants,
        COUNT(b.booking_id) AS booked_places,
        e.max_participants - COUNT(b.booking_id) AS available_places
    FROM public.events e
    LEFT JOIN public.event_bookings b
        ON e.event_id = b.event_id
    WHERE e.event_date >= CURRENT_TIMESTAMP
    GROUP BY e.event_id
    ORDER BY e.event_date ASC;
""")

            rows = cursor.fetchall()

    return [
    {
        "event_id": row[0],
        "event_name": row[1],
        "description": row[2],
        "event_date": row[3],
        "location": row[4],
        "max_participants": row[5],
        "booked_places": row[6],
        "available_places": row[7]
    }
    for row in rows
]

@app.get("/api/my-bookings")
def get_my_bookings(
    current_member: dict = Depends(get_current_member)
):
    member_id = current_member["member_id"]

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT event_id
                FROM public.event_bookings
                WHERE member_id = %s
                ORDER BY event_id;
            """, (member_id,))

            rows = cursor.fetchall()

    return {
        "booked_event_ids": [row[0] for row in rows]
    }

@app.get("/api/my-booking-details")
def get_my_booking_details(
    current_member: dict = Depends(get_current_member)
):
    member_id = current_member["member_id"]

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    b.booking_id,
                    e.event_id,
                    e.event_name,
                    e.event_date,
                    e.location,
                    e.description
                FROM public.event_bookings b
                INNER JOIN public.events e
                    ON b.event_id = e.event_id
                WHERE b.member_id = %s
                    AND e.event_date >= CURRENT_TIMESTAMP
                ORDER BY e.event_date ASC;
            """, (member_id,))

            rows = cursor.fetchall()

    return [
        {
            "booking_id": row[0],
            "event_id": row[1],
            "event_name": row[2],
            "event_date": row[3],
            "location": row[4],
            "description": row[5]
        }
        for row in rows
    ]

@app.post("/api/events/{event_id}/book", status_code=201)
def book_event(
    event_id: int,
    current_member: dict = Depends(get_current_member)
):
    member_id = current_member["member_id"]

    with get_db_connection() as connection:
        with connection.cursor() as cursor:

            # Lock this event while checking and creating the booking.
            cursor.execute("""
                SELECT max_participants
                FROM public.events
                WHERE event_id = %s
                  AND event_date >= CURRENT_TIMESTAMP
                FOR UPDATE;
            """, (event_id,))

            event = cursor.fetchone()

            if event is None:
                raise HTTPException(
                    status_code=404,
                    detail="Upcoming event not found"
                )

            max_participants = event[0]

            # Check whether this member has already booked.
            cursor.execute("""
                SELECT booking_id
                FROM public.event_bookings
                WHERE event_id = %s
                  AND member_id = %s;
            """, (event_id, member_id))

            if cursor.fetchone() is not None:
                raise HTTPException(
                    status_code=409,
                    detail="You have already booked this event"
                )

            # Count existing bookings.
            cursor.execute("""
                SELECT COUNT(*)
                FROM public.event_bookings
                WHERE event_id = %s;
            """, (event_id,))

            booked_places = cursor.fetchone()[0]

            if booked_places >= max_participants:
                raise HTTPException(
                    status_code=409,
                    detail="This event is fully booked"
                )

            # Create the booking.
            cursor.execute("""
                INSERT INTO public.event_bookings
                    (event_id, member_id)
                VALUES (%s, %s)
                RETURNING booking_id;
            """, (event_id, member_id))

            booking_id = cursor.fetchone()[0]

    return {
        "message": "Event booked successfully",
        "booking_id": booking_id,
        "event_id": event_id
    }

@app.delete("/api/events/{event_id}/book")
def cancel_event_booking(
    event_id: int,
    current_member: dict = Depends(get_current_member)
):
    member_id = current_member["member_id"]

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM public.event_bookings
                WHERE event_id = %s
                  AND member_id = %s
                RETURNING booking_id;
            """, (event_id, member_id))

            deleted_booking = cursor.fetchone()

            if deleted_booking is None:
                raise HTTPException(
                    status_code=404,
                    detail="You do not have a booking for this event"
                )

    return {
        "message": "Booking cancelled successfully",
        "event_id": event_id
    }