"""
SQLite database setup via SQLAlchemy.
Tables:
  - sensor_readings : timestamped sensor data from the Pi
  - ml_predictions  : timestamped ML model outputs
"""

import os
from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, String, DateTime, create_engine
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# DB lives alongside this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "..", "krishimitra.db")
DB_URL   = f"sqlite:///{DB_PATH}"

engine       = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id             = Column(Integer, primary_key=True, index=True)
    timestamp      = Column(DateTime, default=datetime.utcnow, index=True)
    air_temp       = Column(Float, nullable=True)
    air_humidity   = Column(Float, nullable=True)
    soil_temp      = Column(Float, nullable=True)
    soil_moisture  = Column(Float, nullable=True)
    soil_ph        = Column(Float, nullable=True)
    light_lux      = Column(Float, nullable=True)


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id              = Column(Integer, primary_key=True, index=True)
    timestamp       = Column(DateTime, default=datetime.utcnow, index=True)
    crop            = Column(String, nullable=True)
    yield_value     = Column(Float, nullable=True)
    irrigation_need = Column(String, nullable=True)
    fertilizer      = Column(String, nullable=True)
    # stored inputs for reference
    n_value         = Column(Float, nullable=True)
    p_value         = Column(Float, nullable=True)
    k_value         = Column(Float, nullable=True)
    state           = Column(String, nullable=True)


def init_db():
    """Create all tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
