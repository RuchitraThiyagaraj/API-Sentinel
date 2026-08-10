"""
main.py
-------
Entry point of the FastAPI backend.

Responsibilities:
1. Create DB tables on startup (via SQLAlchemy models).
2. Wire up the /auth and /apis routers.
3. Start a background scheduler (APScheduler) that runs
   run_monitoring_cycle() every MONITOR_INTERVAL_SECONDS.
4. Enable CORS so the React (Vite) frontend can call this API.

Run with:
    uvicorn main:app --reload
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from database import engine, Base
from routers import auth, apis
from services.monitoring import run_monitoring_cycle

load_dotenv()

MONITOR_INTERVAL_SECONDS = int(os.getenv("MONITOR_INTERVAL_SECONDS", "60"))

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    Base.metadata.create_all(bind=engine)

    scheduler.add_job(
        run_monitoring_cycle,
        "interval",
        seconds=MONITOR_INTERVAL_SECONDS,
        id="monitoring_cycle",
        replace_existing=True,
    )
    scheduler.start()
    print(f"[startup] Monitoring scheduler started (every {MONITOR_INTERVAL_SECONDS}s)")

    yield

    # --- shutdown ---
    scheduler.shutdown()


app = FastAPI(title="API Sentinel", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(apis.router)


@app.get("/")
def root():
    return {"message": "API Sentinel backend is running"}
