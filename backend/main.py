from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy import text

from db import get_db, engine
from models import Base, ConnectionLog, HealthCheckResponse, StatusResponse, get_ist_time

# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Health Check Logging API",
    description="Backend API for logging frontend-backend connection health checks",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StatusLogRequest(BaseModel):
    status: str
    response_time_ms: float


# Health API
@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    current_time = get_ist_time()

    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database not reachable"
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

    return StatusResponse(
        status="UP",
        timestamp=current_time.strftime("%Y-%m-%d %H:%M:%S"),
        timezone="Asia/Kolkata (IST)",
        logs=logs
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
