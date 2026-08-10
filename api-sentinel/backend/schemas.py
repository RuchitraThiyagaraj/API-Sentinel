"""
schemas.py
----------
Pydantic models used for request validation and response shaping.
FastAPI uses these automatically to validate incoming JSON and to
serialize outgoing responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator


# ---------- Auth ----------

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


# ---------- APIs ----------

class ApiCreateRequest(BaseModel):
    name: str
    url: str
    method: str = "GET"
    auth_token: Optional[str] = None

    @field_validator("method")
    @classmethod
    def valid_method(cls, v):
        allowed = {"GET", "POST", "PUT", "DELETE"}
        if v.upper() not in allowed:
            raise ValueError(f"method must be one of {allowed}")
        return v.upper()


class ApiResponse(BaseModel):
    id: int
    name: str
    url: str
    method: str
    created_at: datetime

    # latest known status, computed by the router (not stored redundantly)
    status: Optional[str] = None
    http_status_code: Optional[int] = None
    response_time: Optional[float] = None
    last_checked: Optional[datetime] = None
    uptime: Optional[float] = None

    class Config:
        from_attributes = True


class ApiDetailsResponse(ApiResponse):
    total_checks: int = 0
    successful_checks: int = 0
    failed_checks: int = 0


class MonitoringResultResponse(BaseModel):
    id: int
    status: str
    http_status_code: Optional[int]
    response_time: Optional[float]
    checked_at: datetime

    class Config:
        from_attributes = True


# ---------- LLM Documentation Import ----------

class ImportDocumentationRequest(BaseModel):
    documentation_text: str


class ImportDocumentationResponse(BaseModel):
    name: str
    url: str
    method: str
