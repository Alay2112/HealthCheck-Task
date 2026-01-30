# Day 2 – Staging Discipline & Observability

# Overview
- This documentation describes the observability and Staging-discipline changes add to the backend.
- Goal was to make system behaviout visible, predictable and verifiable wihtout changing the business logic.

## Backend ↔ Database Contract
- Backend verifies database connectivity during startup using a real query.
- If the database is unreachable, the application startup is aborted.
- This prevents the backend from running in a partially healthy state.

## Startup Observability
- Added explicit startup logs:
  - Backend server starting
  - Database connection verified
  - Backend server started successfully
  - Startup failure logs if DB is unreachable

These logs allows immediate understanding the startup health of application.

## API Lifecycle Logs
Added request logging:
- Request start with method and path
- Request completion
- HTTP status code
- Request duration in ms.

This provides visibility into request flow and its latency.

## Database Failure Visibility (Runtime)
- Database connectivity is checked during DB-dependent API calls.
- Database failures are logged explicitly.
- Successful connection logs for DB are not printed to avoid noise.

## Counter Metrics
- Added `/metrics` endpoint to expose count.
- Implemented in-memory counters using FastAPI `app.state`:
  - Total commited requests count
  - Failed request count if `status_code` >= 400

Counter restarts when application is restarted and is intended for staging visibility only.

## Note 
- I have made `/health` database independent and it reports process level health.
- While `/status` is database dependent and fails if DB fails.

This is because if `/health` is separated from DB, then whenever `/health` status is okay and DB is failed then we can identify that there is onyl DB issue and we will restart the database services while if `/health` fails, we can identify that backend is crashed and it needs restart.
