import models
import prediction
import schemas
from sqlalchemy import text
from models import SleepReadingDB, PatientDB
from database import SessionLocal
from schemas import  SleepReadingCreate, SleepReadingUpdate, SleepReadingResponse, \
     PatientCreate, PatientUpdate, PatientResponse, PredictionResponse
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
app = FastAPI(title="Sleep Quality API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# patients' endpoints
anyway@app.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED )
def creat_patient(patient: PatientCreate, db: Session= Depends(get_db)):
    new_patient = PatientDB(**patient.model_dump())
    db.add(new_patient)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Email '{patient.email}' is already registered")
    db.refresh(new_patient)
    return new_patient

@app.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Patient {patient_id} not found")
    return patient

# pagination: means results come back in chunks (pages) instead of all at once
# limit(max rows to return), offset(how many rost to skip before starting)
@app.get("/patients", response_model=list[PatientResponse])
def list_patient(
        limit: int = Query(20, ge=1, le=100, descriptions="Max rows returned"),
        offset: int= Query(0, ge=0, description="Rows to skip"),
        db: Session = Depends(get_db),
):
    return (
        db.query(models.PatientDB).order_by(models.PatientDB.id).offset(offset).limit(limit).all()
    )

# readings endpoints
@app.post("/readings", response_model=SleepReadingResponse, status_code=status.HTTP_201_CREATED)
def create_reading(reading: SleepReadingCreate, db: Session = Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.id == reading.patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail=f"patient {reading.patient_id} not found")

    new_reading = SleepReadingDB(**reading.model_dump())
    db.add(new_reading)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
            detail="A reading for this patient at this recorded_at already exists",)
    db.refresh(new_reading)
    return new_reading


@app.get("/patients/{patient_id}/readings", response_model=list[SleepReadingResponse])
def get_patient_readings(patient_id: int, db: Session = Depends(get_db),limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)):
    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found ")
    return (
        db.query(SleepReadingDB)
        .filter(SleepReadingDB.patient_id == patient_id)
        .order_by(SleepReadingDB.record_at)
        .offset(offset)
        .limit(limit)
        .all()
    ) # or we can also use without offset and limit: return patient.readings

@app.get("/patient/{patient_id}/readings", response_model=list[SleepReadingResponse])
def get_patient_readings(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found ")
    return patient.readings


# return all readings

@app.get("/readings", response_model=list[SleepReadingResponse])
def get_readings( limit: int = Query(20, ge=1, le=100, description="Max rows returned"),
        offset: int= Query(0, ge=0, description="Rows to skip"),
        db: Session = Depends(get_db)):
    return (
        db.query(SleepReadingDB).order_by(SleepReadingDB.record_at)
        .offset(offset)
        .limit(limit)
        .all()
    )



# prediction endpoint

@app.get("/readings/{reading_id}/prediction", response_model=PredictionResponse)
def get_prediction(reading_id: int, db: Session = Depends(get_db)):
    reading = db.query(SleepReadingDB).filter(SleepReadingDB.id == reading_id).first()
    if reading is None:
        raise HTTPException(status_code=404, detail=f"Reading {reading_id} not found")
    result =  prediction.predict_quality(sleep_duration_hours=reading.sleep_duration_hours,
                                      heart_rate= reading.heart_rate,
                                      is_deep_sleep= reading.is_deep_sleep)
    return schemas.PredictionResponse(
        reading_id = reading.id,
        model_version=prediction.MODEL_VERSION,
        **result,
    )

@app.get("/health")
def get_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail={"status": "unhealthy", "database": "unreachable"})
    return {"status": "ok", "database": "connected"}


# patch and delete patient

@app.patch("/patients/{patient_id}", response_model=PatientResponse)
def patch_patient(patient_id: int, patient: PatientUpdate, db: Session = Depends(get_db)):
    patient_existing = db.query(PatientDB).filter(PatientDB.id == patient_id).first()

    if patient_existing is None:
        raise HTTPException(status_code=404, detail= f"patient {patient_id} not found")

    for field, value in patient.model_dump(exclude_unset=True).items():
        if value is None:
            raise HTTPException(status_code=422,
                                detail=f"Field '{field}' cannot be set to null")
        setattr(patient_existing, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{patient_existing.email}' is already registered",
        )

    db.refresh(patient_existing)
    return patient_existing

@app.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(PatientDB).filter(PatientDB.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail= f"patient {patient_id} not found")

    db.delete(patient)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete patient {patient_id}: they have existing sleep readings",
        )





# patch and delete patient_readings

@app.patch("/readings/{reading_id}", response_model=SleepReadingResponse)
def patch_reading(reading_id: int,  reading: SleepReadingUpdate, db: Session = Depends(get_db)):
    existing_reading = db.query(SleepReadingDB).filter(SleepReadingDB.id == reading_id).first()

    if existing_reading is None:
        raise HTTPException(status_code=404, detail=f"reading '{reading_id}' not found")

    for field, value in reading.model_dump(exclude_unset=True).items():
        if value is None and field != "raw_device_data":
            raise HTTPException(status_code=422, detail=f"Field {field} cannot be set to null")
        setattr(existing_reading, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="update conflicts with an existing reading for this patinet/time")
    db.refresh(existing_reading)
    return existing_reading


@app.delete("/readings/{reading_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reading(reading_id: int, db: Session = Depends(get_db)):
    reading = db.query(SleepReadingDB).filter(SleepReadingDB.id == reading_id).first()
    if reading is None:
        raise HTTPException(status_code=404, detail=f"Reading with id {reading_id} not found")
    db.delete(reading)
    db.commit()

























































































