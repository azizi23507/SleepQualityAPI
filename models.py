from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    ForeignKey, TIMESTAMP, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class PatientDB(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    readings = relationship("SleepReadingDB", back_populates="patient")

    __table_args__ = (
        CheckConstraint("age > 0 AND age < 130", name="check_age_range"),
    )

class SleepReadingDB(Base):
    __tablename__ = "sleep_readings"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer,
                        ForeignKey("patients.id", ondelete="RESTRICT")
                        , nullable=False)
    sleep_duration_hours = Column(Float, nullable=False)
    heart_rate = Column(Float, nullable=False)
    is_deep_sleep = Column(Boolean, nullable=False, server_default="false")
    record_at = Column(TIMESTAMP, server_default=func.now())
    raw_device_data = Column(JSONB, nullable=True)

    patient = relationship("PatientDB", back_populates="readings")

    __table_args__ = (
        CheckConstraint("sleep_duration_hours > 0 AND sleep_duration_hours < 24",
                        name="check_sleep_duration_hours_range"
                        ),
        CheckConstraint("heart_rate > 20 AND heart_rate < 220",
                        name="check_heart_rate_range"
                        ),
    )
