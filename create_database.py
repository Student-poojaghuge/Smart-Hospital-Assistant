from database.database import engine, Base
from database.models import (
    User,
    Patient,
    Doctor,
    Appointment,
    MedicalRecord,
    EmergencyAssessment,
    Prediction,
    Medicine,
    Hospital,
    ChatHistory
)

Base.metadata.create_all(bind=engine)

print("✅ Database created successfully!")