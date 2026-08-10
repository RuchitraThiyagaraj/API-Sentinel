# API Sentinel — Real-Time API Health & Performance Monitoring

A simple full-stack app to monitor whether your APIs are online, how fast
they respond, and to alert you by email when one keeps failing.

## The complete flow

```
User -> Register/Login (JWT) -> Dashboard -> Add API (manual or paste docs -> LLM extracts fields)
     -> FastAPI validates (Pydantic) -> SQLAlchemy saves API -> MySQL
     -> Background scheduler (APScheduler) checks every API on an interval
     -> times the HTTP request -> determines Online/Offline/Slow
     -> SQLAlchemy saves a MonitoringResult row -> MySQL
     -> React Dashboard fetches /apis -> shows status, response time, uptime
     -> API Details page fetches /apis/{id}/history -> Recharts graph + table
     -> 3 consecutive failures -> backend sends an email alert
```

## Database (3 tables)

- **users**: id, name, email, password_hash
- **apis**: id, user_id, name, url, method, created_at (+ consecutive_failures counter)
- **monitoring_results**: id, api_id, status, http_status_code, response_time, checked_at

`User 1---N Api 1---N MonitoringResult`

## Setup

### 1. MySQL
```sql
CREATE DATABASE api_sentinel;
```

### 2. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in DATABASE_URL, JWT_SECRET_KEY, SMTP_*, ANTHROPIC_API_KEY
uvicorn main:app --reload
```
Tables are created automatically on startup. Docs at http://localhost:8000/docs

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
App runs at http://localhost:5173

## Notes

- The LLM (services/llm.py) is used **only** to extract `{name, url, method}`
  from pasted documentation — it never performs monitoring. If it's not
  configured or fails, manual "Add API" still works normally.
- The background monitor (services/monitoring.py) runs via APScheduler,
  scheduled inside `main.py`'s lifespan startup, every
  `MONITOR_INTERVAL_SECONDS` (default 60s).
- Emails (services/email.py) are only sent by the backend, after 3
  consecutive offline checks for the same API.
- Every `/apis` endpoint checks `api.user_id == current_user.id` so users
  only ever see their own APIs.
