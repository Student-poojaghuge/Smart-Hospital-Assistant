
import streamlit as st
import requests
import pandas as pd
from theme import apply_hospital_theme

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Admin Dashboard | Smart Hospital",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_hospital_theme()
# =====================================================
# SHARED SIDEBAR NAVIGATION
# =====================================================

with st.sidebar:
    st.markdown("## 🏥 Smart Hospital")
    st.caption("Administration Workspace")
    st.divider()

    st.markdown("### Navigation")

    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("main.py")

    if st.button("👨‍⚕️ Doctor Dashboard", use_container_width=True):
        st.switch_page("pages/doctor_dashboard.py")

    if st.button("🧑 Patient Dashboard", use_container_width=True):
        st.switch_page("pages/patient_dashboard.py")

    if st.button("📅 Appointments", use_container_width=True):
        st.switch_page("pages/appointments.py")

    if st.button("🤖 Medical AI Assistant", use_container_width=True):
        st.switch_page("pages/medical_assistant.py")

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")

API_URL = "http://127.0.0.1:8001"
TIMEOUT = 15


# =====================================================
# HEADER
# =====================================================

st.markdown("""
<div class="brand-header">
    <div class="brand-icon">🏥</div>
    <div>
        <div class="brand-name">Smart Hospital</div>
        <div class="brand-subtitle">ADMINISTRATION WORKSPACE</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.title("Admin Dashboard")

st.markdown("""
<div class="welcome-panel">
    <div style="font-size:20px;font-weight:750;color:#16385f;">
        Hospital System Overview
    </div>
    <div style="color:#71859a;font-size:13px;margin-top:5px;">
        Monitor system activity, users, doctors, hospitals,
        appointments, medical records, and medicines.
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# API HELPER
# =====================================================

def get_api_data(endpoint, data_key=None):
    """Fetch data from an existing backend endpoint."""
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=TIMEOUT,
        )

        if response.status_code != 200:
            st.error(
                f"Could not load {endpoint}. "
                f"HTTP status: {response.status_code}"
            )
            return None

        data = response.json()

        if data_key:
            return data.get(data_key, [])

        return data

    except requests.exceptions.ConnectionError:
        st.error(
            "Backend server is not running. "
            "Start FastAPI on port 8001."
        )
        st.stop()

    except requests.exceptions.Timeout:
        st.error(f"Request timed out while loading {endpoint}.")
        return None

    except (requests.exceptions.RequestException, ValueError) as exc:
        st.error(f"Error loading {endpoint}: {exc}")
        return None

# =====================================================
# SYSTEM STATISTICS
# =====================================================

st.markdown(
    '<div class="section-heading">📊 System Statistics</div>',
    unsafe_allow_html=True,
)

dashboard_data = get_api_data("/admin/dashboard")

statistics = {}

if isinstance(dashboard_data, dict):
    statistics = dashboard_data.get("statistics", {}) or {}

if statistics:
    metric_items = [
        ("Total Users", "total_users"),
        ("Total Doctors", "total_doctors"),
        ("Total Patients", "total_patients"),
        ("Total Hospitals", "total_hospitals"),
        ("Appointments", "total_appointments"),
        ("Medical Records", "total_medical_records"),
        ("Emergency Assessments", "total_emergency_assessments"),
        ("Total Medicines", "total_medicines"),
        ("Chat History", "total_chat_history"),
    ]

    for start in range(0, len(metric_items), 3):
        cols = st.columns(3, gap="medium")

        for col, (label, key) in zip(
            cols,
            metric_items[start:start + 3],
        ):
            with col:
                st.metric(label, statistics.get(key, 0))
else:
    st.info("Statistics are unavailable. Check the backend response.")

# =====================================================
# DATA TABLE HELPER
# =====================================================

def display_table(title, endpoint, data_key, empty_message):
    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True,
    )

    data = get_api_data(endpoint, data_key)

    if data is None:
        return

    if not data:
        st.info(empty_message)
        return

    if isinstance(data, list):
        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("The server returned data in an unexpected format.")

# =====================================================
# MANAGEMENT NAVIGATION
# =====================================================

st.divider()

st.markdown(
    '<div class="section-heading">🗂️ Management Centre</div>',
    unsafe_allow_html=True,
)

section = st.radio(
    "Choose a management section",
    [
        "Users",
        "Doctors",
        "Hospitals",
        "Appointments",
        "Medical Records",
        "Medicines",
    ],
    horizontal=True,
    label_visibility="collapsed",
)

# =====================================================
# USER MANAGEMENT
# =====================================================

if section == "Users":
    display_table(
        "👥 User Management",
        "/admin/users",
        "users",
        "No users found.",
    )

# =====================================================
# DOCTOR MANAGEMENT
# =====================================================

elif section == "Doctors":
    display_table(
        "👨‍⚕️ Doctor Management",
        "/doctors/",
        "doctors",
        "No doctors found.",
    )

# =====================================================
# HOSPITAL MANAGEMENT
# =====================================================

elif section == "Hospitals":
    display_table(
        "🏥 Hospital Management",
        "/hospitals/",
        "hospitals",
        "No hospitals found.",
    )

# =====================================================
# APPOINTMENT MANAGEMENT
# =====================================================

elif section == "Appointments":
    display_table(
        "📅 Appointment Management",
        "/admin/appointments",
        "appointments",
        "No appointments found.",
    )

# =====================================================
# MEDICAL RECORDS MANAGEMENT
# =====================================================

elif section == "Medical Records":
    display_table(
        "📋 Medical Records Management",
        "/admin/medical-records",
        "medical_records",
        "No medical records found.",
    )

# =====================================================
# MEDICINE MANAGEMENT
# =====================================================

elif section == "Medicines":
    display_table(
        "💊 Medicine Management",
        "/admin/medicines",
        "medicines",
        "No medicines found.",
    )

# =====================================================
# FOOTER
# =====================================================

st.markdown("""
<div class="footer-text">
    Smart Hospital Management System
    <br>
    Administration Workspace · AI-Powered Healthcare
</div>
""", unsafe_allow_html=True)
