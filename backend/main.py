from fastapi import FastAPI
from backend.routes import auth
from backend.routes import patients
from backend.routes import health_assessment
from backend.routes import doctors
from backend.routes import appointments
from backend.routes import medical_records
from backend.routes import medicines
from backend.routes import heart_disease
app = FastAPI(
    title="Smart Hospital Assistant API",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(health_assessment.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(medical_records.router)
app.include_router(medicines.router)
app.include_router(heart_disease.router)

@app.get("/")
def home():
    return {
        "message": "Smart Hospital Assistant API is running"
    }