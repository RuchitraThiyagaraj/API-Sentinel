"""
services/monitoring.py
-----------------------
The core background feature of API Sentinel.

check_api(api)      -> performs ONE health check against a single API
                        and saves a MonitoringResult row.

run_monitoring_cycle() -> loops over every API in the database and
                        calls check_api() on each one. This function is
                        what the scheduler (see main.py) calls repeatedly.

Flow (matches the spec exactly):

Background Task
 -> Send HTTP request
 -> Start timer
 -> Receive response
 -> Stop timer
 -> Calculate response time
 -> Check HTTP status
 -> Determine Online / Offline / Slow
 -> SQLAlchemy
 -> Save result into MySQL
 -> (if 3 consecutive failures) send email alert
"""

import os
import time
import requests
from dotenv import load_dotenv

from database import SessionLocal
import models
from services.email import send_failure_alert

load_dotenv()

SLOW_RESPONSE_THRESHOLD_MS = float(os.getenv("SLOW_RESPONSE_THRESHOLD_MS", "1000"))
FAILURE_THRESHOLD = 3  # consecutive failures before an email alert is sent


def _determine_status(success: bool, response_time_ms: float) -> str:
    if not success:
        return "offline"
    if response_time_ms > SLOW_RESPONSE_THRESHOLD_MS:
        return "slow"
    return "online"


def check_api(db, api: models.Api) -> models.MonitoringResult:
    """
    Performs a single HTTP check for one API row and persists the result.
    `db` is an existing SQLAlchemy session (so callers can batch commits).
    """
    headers = {}
    if api.auth_token:
        headers["Authorization"] = f"Bearer {api.auth_token}"

    http_status_code = None
    response_time_ms = None
    error_message = None
    success = False

    start = time.perf_counter()
    try:
        response = requests.request(
            method=api.method,
            url=api.url,
            headers=headers,
            timeout=10,
        )
        response_time_ms = (time.perf_counter() - start) * 1000
        http_status_code = response.status_code
        success = response.ok  # True for 2xx/3xx
    except requests.RequestException as e:
        response_time_ms = (time.perf_counter() - start) * 1000
        error_message = str(e)
        success = False

    status = _determine_status(success, response_time_ms)

    result = models.MonitoringResult(
        api_id=api.id,
        status=status,
        http_status_code=http_status_code,
        response_time=round(response_time_ms, 2) if response_time_ms else None,
        error_message=error_message,
    )
    db.add(result)

    # --- consecutive failure tracking -> email alert ---
    if status == "offline":
        api.consecutive_failures += 1
    else:
        api.consecutive_failures = 0

    db.commit()
    db.refresh(result)

    if api.consecutive_failures == FAILURE_THRESHOLD:
        send_failure_alert(
            api_name=api.name,
            api_url=api.url,
            last_http_status=http_status_code,
            failure_count=api.consecutive_failures,
        )

    return result


def run_monitoring_cycle():
    """
    Called on a schedule (see main.py's APScheduler job).
    Opens its own DB session since it runs outside of any request.
    """
    db = SessionLocal()
    try:
        apis = db.query(models.Api).all()
        for api in apis:
            try:
                check_api(db, api)
            except Exception as e:
                # one bad API should never stop the whole monitoring cycle
                print(f"[monitoring] Error checking API {api.id} ({api.name}): {e}")
    finally:
        db.close()
