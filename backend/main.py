import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy import text
from db.db import get_db, SessionLocal
from db.models import ConnectionLog, HealthCheckResponse, StatusResponse, get_ist_time
import logging
import json
import time


# Simulation failure objects
SIMULATE_DB_DOWN = os.getenv("SIMULATE_DB_DOWN", "false").lower() == "true"
SIMULATE_CRASH = os.getenv("SIMULATE_CRASH", "false").lower() == "true"

# log objects
logging.basicConfig(level=logging.INFO,
                    handlers=[logging.StreamHandler()],
                    )

logger_1 = logging.getLogger("/status")
startup_log = logging.getLogger("startup")
failure_log = logging.getLogger("simulate-failure")
api_logs = logging.getLogger("request")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )


class StatusLogRequest(BaseModel):
    status: str
    response_time_ms: float


# For creating startup logs
@app.on_event("startup")
async def startup_event():

    app.state.request_count = 0
    app.state.failed_request_count = 0

    startup_log.info(json.dumps({'level': 'INFO', 'message': 'Backend server starting...'}))

    if SIMULATE_CRASH:
        startup_log.warning(json.dumps({'level': 'WARNING', 'message': 'Backend is crashed and going down...'}))
        raise RuntimeError('Backend crashed intentionally!')

    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
        startup_log.info(json.dumps({'level': 'INFO', 'message': 'DB connection verified!'}))
        startup_log.info(json.dumps({'level': 'INFO', 'message': 'Backend server started!'}))

    except Exception as e:
        startup_log.error(json.dumps({'level': 'ERROR', 'message': f'Backend startup failed!: {e}'}))
        raise RuntimeError("Startup aborted due to DB failure")

    finally:
        db.close()


# Request life cycle
@app.middleware("http")
async def request_logs(request, call_next):
    app.state.request_count += 1
    start = time.time()

    api_logs.info(json.dumps({'level': 'INFO',
                              'message': f'Request Started: {request.method}, {request.url.path}'}))

    response = await call_next(request)

    if response.status_code >= 400:
        app.state.failed_request_count += 1

    duration = round((time.time()-start)*1000, 2)

    api_logs.info(json.dumps({'level': 'INFO',
                              'message': f'Request completed: {request.method}, {request.url.path}',
                              'status_code': response.status_code,
                              'duration_ms': duration}))
    return response


# Health API
@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    current_time = get_ist_time()

    return HealthCheckResponse(
        status="UP",
        timestamp=current_time.strftime("%Y-%m-%d %H:%M:%S"),
        timezone="Asia/Kolkata (IST)"
    )


# Status API
@app.post("/status", response_model=StatusResponse, tags=["Health"])
async def status_check(payload: StatusLogRequest, db: Session = Depends(get_db)):
    current_time = get_ist_time()

    if SIMULATE_DB_DOWN:
        failure_log.warning(json.dumps({"level": "WARNING", "message": "SIMULATE_DB_DOWN enabled"}))
        raise HTTPException(
            status_code=503,
            detail="Simulate DB failure!"
            )

    try:
        db.execute(text("SET statement_timeout = 1000"))
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger_1.error(json.dumps({'level': 'ERROR', 'message': f'DB connection failed!!: {e}'}))
        raise HTTPException(
            status_code=503,
            detail="Database not reachable!"
            )

    try:
        # Save log into DB using REAL response time sent by frontend
        db_log = ConnectionLog(
            status=payload.status,
            response_time_ms=payload.response_time_ms,
            checked_at=current_time
        )

        db.add(db_log)
        db.commit()
        db.refresh(db_log)

        # Return all logs
        logs = db.query(ConnectionLog).order_by(ConnectionLog.checked_at.desc()).limit(10).all()

        logger_1.info(json.dumps({'level': 'INFO', 'message': 'Status logs posted into table successfully'}))

        return StatusResponse(
            status="UP",
            timestamp=current_time.strftime("%Y-%m-%d %H:%M:%S"),
            timezone="Asia/Kolkata (IST)",
            logs=logs
        )
    except Exception as e:
        logger_1.error(json.dumps({'level': 'ERROR', 'message': f'Error while posting data into table: {e}'}))
        raise HTTPException(
            status_code=503,
            detail="Failed to save status logs"
        )


# Endpoint for counter Optional
@app.get("/metrics")
def metrics():
    return {
        "TOTAL REQUESTS": app.state.request_count,
        "FAILED REQUESTS": app.state.failed_request_count
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
