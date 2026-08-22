import random
from datetime import datetime, timedelta

from database import SessionLocal
from models import PatientDB, SleepReadingDB

PATIENTS = [
    {"name": "Anna Keller", "age": 34, "email": "anna.keller@example.com"},
    {"name": "Ben Fischer", "age": 41, "email": "ben.fischer@example.com"},
    {"name": "Clara Weber", "age": 27, "email": "clara.weber@example.com"},
]


def seed():
    db = SessionLocal()
    try:
        if db.query(PatientDB).first():
            print("Database already seeded, skipping.")
            return

        for data in PATIENTS:
            patient = PatientDB(**data)
            db.add(patient)
            db.flush()  # assigns patient.id without committing yet

            for days_ago in range(14):
                db.add(SleepReadingDB(
                    patient_id=patient.id,
                    sleep_duration_hours=round(random.uniform(5.0, 9.0), 1),
                    heart_rate=round(random.uniform(50.0, 75.0), 1),
                    is_deep_sleep=random.choice([True, False]),
                    raw_device_data={"device": "demo-tracker", "battery": random.randint(20, 100)},
                    record_at=datetime.now() - timedelta(days=days_ago),
                ))

        db.commit()
        print(f"Seeded {len(PATIENTS)} patients with 14 readings each.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()