import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy import text
from db.db import get_db
from db.models import ConnectionLog, HealthCheckResponse, StatusResponse, get_ist_time
import logging
import json
import time

# Simulation failure objects
SIMULATE_DB_DOWN= os.getenv("SIMULATE_DB_DOWN", "false").lower()=="true"
SIMULATE_CRASH= os.getenv("SIMULATE_CRASH", "false").lower()=="true"

# log objects
logging.basicConfig(level=logging.INFO,
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler('./logs/logs.txt')
                        ],
                    )

logger_1= logging.getLogger("/health")
logger_2= logging.getLogger("/status")
startup_log= logging.getLogger("startup")
failure_log= logging.getLogger("simulate-failure")
api_logs= logging.getLogger("request")

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

    startup_log.info(json.dumps({'level': 'INFO', 'message': 'Backend server started!'}))
    if SIMULATE_CRASH:
        startup_log.warning(json.dumps({'level': 'WARNING', 'message': 'Backend is crashed and going down...'}))
        raise RuntimeError('Backend crashed!')

    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        startup_log.info(json.dumps({'level': 'INFO', 'message': 'Database Connection Successful!'}))
    except Exception as e:
        startup_log.error(json.dumps({'level': 'ERROR', 'message': f'Database Connection Failed! : {e}'}))


# Request life cycle
@app.middleware("http")
async def request_logs(request, call_next):
    start=time.time()

    api_logs.info(json.dumps({'level': 'INFO',
                              'message': f'Request Started: {request.method}, {request.url.path}'}))

    response = await call_next(request)

    duration = round((time.time()-start)*1000, 2)

    api_logs.info(json.dumps({'level': 'INFO',
                              'message': f'Request completed: {request.method}, {request.url.path}',
                              'status_code': response.status_code,
                              'duration_ms': duration}))
    return response


# Health API
@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    current_time = get_ist_time()

    if SIMULATE_DB_DOWN:
        failure_log.warning(json.dumps({"level": "WARNING", "message": "SIMULATE_DB_DOWN enabled"}))
        raise HTTPException( status_code=503, detail="Simulate DB failure!")
    
    try:
        db.execute(text("SELECT 1"))
        
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database not reachable!"
        )
    
    return HealthCheckResponse(
        status="UP",
        timestamp=current_time.strftime("%Y-%m-%d %H:%M:%S"),
        timezone="Asia/Kolkata (IST)"
    )


# Status API
@app.post("/status", response_model=StatusResponse, tags=["Health"])
async def status_check(payload: StatusLogRequest, db: Session = Depends(get_db)):
    current_time = get_ist_time()

    try:
    # Save log into DB using REAL response time sent by frontend
        db_log = ConnectionLog(
            status=payload.status,
            response_time_ms=payload.response_time_ms,
            checked_at=current_time
        )

        db.add(db_log)
        db.commit()

    # Return all logs
        logs = db.query(ConnectionLog).order_by(ConnectionLog.checked_at.desc()).limit(10).all()

        logger_2.info(json.dumps({'level': 'INFO', 'message': 'Status logs posted into table successfully'}))

        return StatusResponse(
            status="UP",
            timestamp=current_time.strftime("%Y-%m-%d %H:%M:%S"),
            timezone="Asia/Kolkata (IST)",
            logs=logs
        )
    except Exception as e:
        logger_2.error(json.dumps({'level': 'ERROR', 'message': f'Error while posting data into table: {e}'}))
        raise HTTPException(
            status_code=500,
            detail="Failed to save status logs"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
