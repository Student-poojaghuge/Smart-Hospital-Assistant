from fastapi import FastAPI
from backend.routes import auth
from backend.routes import patients
from backend.routes import health_assessment
from backend.routes import doctors
from backend.routes import appointments
from backend.routes import medical_records
from backend.routes import medicines
from backend.routes import heart_disease
from backend.routes import diabetes
from backend.routes import emergency
from backend.routes import disease
from backend.routes import predictions
from backend.routes import disease_knowledge
from backend.routes import disease_assistant
from backend.routes import hospitals
from backend.routes import medical_knowledge
from backend.routes import emergency_knowledge
from backend.routes import rag
from backend.routes import chat_history
from backend.routes import symptom
from backend.routes import admin

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
app.include_router(diabetes.router)
app.include_router(emergency.router)
app.include_router(disease.router)
app.include_router(predictions.router)
app.include_router(disease_knowledge.router)
app.include_router(disease_assistant.router)
app.include_router(hospitals.router)
app.include_router(medical_knowledge.router)
app.include_router(emergency_knowledge.router)
app.include_router(rag.router)
app.include_router(chat_history.router)
app.include_router(symptom.router)
app.include_router(admin.router)


@app.get("/")
def home():
    return {
        "message": "Smart Hospital Assistant API is running"
    }
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Smart Hospital Assistant API is running"
    }