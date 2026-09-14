from sqlalchemy import Column, Integer, String, Text
from database.database import Base


# =========================
# USER
# =========================
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)


# =========================
# PATIENT
# =========================
class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    age = Column(Integer)
    gender = Column(String(20))
    phone = Column(String(20))
    blood_group = Column(String(10))
    address = Column(Text)


# =========================
# DOCTOR
# =========================
class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    specialization = Column(String(100))
    qualification = Column(String(150))
    experience = Column(Integer)
    phone = Column(String(20))
    hospital_name = Column(String(150))


# =========================
# APPOINTMENT
# =========================
class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    doctor_id = Column(Integer, nullable=False)
    appointment_date = Column(String(20), nullable=False)
    appointment_time = Column(String(20), nullable=False)
    reason = Column(Text)
    status = Column(String(30), default="Pending")
    notes = Column(Text)


# =========================
# MEDICAL RECORD
# =========================
class MedicalRecord(Base):
    __tablename__ = "medical_records"

    record_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    doctor_id = Column(Integer)
    record_date = Column(String(20), nullable=False)
    symptoms = Column(Text)
    diagnosis = Column(Text)
    allergies = Column(Text)
    existing_conditions = Column(Text)
    doctor_notes = Column(Text)


# =========================
# EMERGENCY ASSESSMENT
# =========================
class EmergencyAssessment(Base):
    __tablename__ = "emergency_assessments"

    assessment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    assessment_date = Column(String(20), nullable=False)

    heart_rate = Column(Integer)
    systolic_bp = Column(Integer)
    diastolic_bp = Column(Integer)
    temperature = Column(String(20))
    oxygen_level = Column(Integer)

    symptoms = Column(Text)
    risk_score = Column(String(20))
    emergency_level = Column(String(30))
    ai_recommendation = Column(Text)


# =========================
# PREDICTION
# =========================
class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    prediction_date = Column(String(20), nullable=False)

    prediction_type = Column(String(50), nullable=False)
    predicted_result = Column(String(200), nullable=False)
    confidence_score = Column(String(20))
    model_name = Column(String(100))
    explanation = Column(Text)


# =========================
# MEDICINE
# =========================
class Medicine(Base):
    __tablename__ = "medicines"

    medicine_id = Column(Integer, primary_key=True, index=True)
    medicine_name = Column(String(150), nullable=False)
    generic_name = Column(String(150))
    category = Column(String(100))
    uses = Column(Text)
    precautions = Column(Text)
    side_effects = Column(Text)
    prescription_required = Column(String(10), default="Yes")
    doctor_verified = Column(String(10), default="No")