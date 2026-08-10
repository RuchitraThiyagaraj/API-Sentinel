"""
models.py
---------
SQLAlchemy ORM models -> the 3 tables described in the spec:

    users
    apis
    monitoring_results

Relationships:
    User  --1:N-->  Api  --1:N-->  MonitoringResult
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    apis = relationship("Api", back_populates="owner", cascade="all, delete-orphan")


class Api(Base):
    __tablename__ = "apis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String(150), nullable=False)
    url = Column(String(500), nullable=False)
    method = Column(String(10), default="GET", nullable=False)
    auth_token = Column(String(500), nullable=True)  # optional Authorization header

    # tracks consecutive failures so we know when to send an email alert
    consecutive_failures = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="apis")
    monitoring_results = relationship(
        "MonitoringResult", back_populates="api", cascade="all, delete-orphan"
    )


class MonitoringResult(Base):
    __tablename__ = "monitoring_results"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("apis.id"), nullable=False)

    status = Column(String(20), nullable=False)          # "online" | "offline" | "slow"
    http_status_code = Column(Integer, nullable=True)     # null if request failed entirely
    response_time = Column(Float, nullable=True)          # milliseconds
    error_message = Column(Text, nullable=True)

    checked_at = Column(DateTime(timezone=True), server_default=func.now())

    api = relationship("Api", back_populates="monitoring_results")
