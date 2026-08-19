from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from typing import Any

# patient

class PatientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., gt=0, lt=130)
    email: EmailStr

class PatientCreate(PatientBase):
    # What the client sends to create a patient.
    pass

class PatientUpdate(BaseModel):
    # What the client sends to PATCH a patient. Every field optional —
    # only fields actually included get changed.
    name: str | None = Field(None, min_length=1, max_length=100)
    age: int | None = Field(None, gt=0, lt=130)
    email: EmailStr | None = None

class PatientResponse(PatientBase):
    # What the API sends back
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Sleep Readings

class SleepReadingBase(BaseModel):
    patient_id: int
    sleep_duration_hours: float = Field(..., gt=0, le=24)
    heart_rate: float = Field(..., gt=20, lt=220)
    is_deep_sleep: bool = False
    raw_device_data: dict[str, Any] | None = None

class SleepReadingCreate(SleepReadingBase):
    #What the client sends to create a reading.
    pass

class SleepReadingUpdate(BaseModel):
    # What the client sends to PATCH a reading. Every field optional.
    # patient_id intentionally excluded — a reading shouldn't be
    # reassigned to a different patient via update

    sleep_duration_hours: float | None = Field(None, gt=0, le=24)
    heart_rate: float | None = Field(None, gt=20, lt=220)
    is_deep_sleep: bool | None = None
    raw_device_data: dict[str, Any] | None = None

class SleepReadingResponse(SleepReadingBase):
    # What the API sends back.
    id: int
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)