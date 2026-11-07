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


class MemberRegistration(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=12)
    confirm_password: str


@app.get("/api/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {
        "status": "ok",
        "application": "Forewalk Games"
    }


@app.post("/api/register")
def register_member(member: MemberRegistration):
    """Register a new member with validated data."""
    if member.password != member.confirm_password:
        raise HTTPException(
            status_code=422,
            detail="Passwords do not match"
        )

    return {
        "message": "Registration data validated successfully",
        "email": member.email
    }