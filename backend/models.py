from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel
from datetime import datetime
import pytz

Base = declarative_base()


# ✅ DB Table
class ConnectionLog(Base):
    __tablename__ = "connection_logs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    checked_at = Column(DateTime, nullable=False)


# ✅ Response Models
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    timezone: str


class ConnectionLogResponse(BaseModel):
    id: int
    status: str
    response_time_ms: float
    checked_at: datetime

    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    status: str
    timestamp: str
    timezone: str
    logs: list[ConnectionLogResponse]


def get_ist_time():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist)
