import html
import json
import sys
from datetime import date, time
from pathlib import Path
from urllib.parse import quote

import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_mic_recorder import speech_to_text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_ROOT / "app"
sys.path.insert(0, str(APP_DIR))

from translations import get_text
from accessibility import apply_accessibility
from theme import apply_hospital_theme


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Patient Dashboard",
    page_icon="👤",
    layout="wide",
)

apply_hospital_theme()

API_URL = "http://127.0.0.1:8001"
language = st.session_state.get("language", "English")

LANGUAGE_CODES = {
    "English": "en-US",
    "Marathi": "mr-IN",
    "Hindi": "hi-IN",
}

speech_language = LANGUAGE_CODES.get(language, "en-US")


# =========================================================
# TEXT-TO-SPEECH FUNCTION
# =========================================================

def add_speaker_button(
    text_to_read,
    button_label="🔊 Read Aloud",
    language_code="en-US",
):
    """Read text using the browser's speech synthesis."""

    if not text_to_read or not str(text_to_read).strip():
        st.info("No text available to read.")
        return

    speech_text = json.dumps(
        str(text_to_read),
        ensure_ascii=True,
    )

    speech_text = (
        speech_text
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )

    speech_language_json = json.dumps(language_code)
    safe_button_label = html.escape(button_label)

    components.html(
        f"""
        <div style="font-family:sans-serif;">
            <button id="speak"
                style="padding:9px 14px;border-radius:8px;
                cursor:pointer;font-size:15px;">
                {safe_button_label}
            </button>

            <button id="stop"
                style="padding:9px 14px;border-radius:8px;
                cursor:pointer;font-size:15px;margin-left:6px;">
                ⏹️ Stop Reading
            </button>
        </div>

        <script>
            const textToRead = {speech_text};
            const languageCode = {speech_language_json};

            document.getElementById("speak").onclick = function() {{
                if (!("speechSynthesis" in window)) {{
                    alert("Text-to-speech is not supported by this browser.");
                    return;
                }}

                window.speechSynthesis.cancel();

                const message = new SpeechSynthesisUtterance(textToRead);
                message.lang = languageCode;
                message.rate = 0.9;

                window.speechSynthesis.speak(message);
            }};

            document.getElementById("stop").onclick = function() {{
                if ("speechSynthesis" in window) {{
                    window.speechSynthesis.cancel();
                }}
            }};
        </script>
        """,
        height=60,
    )


# =========================================================
# APPOINTMENT STATUS BADGE
# =========================================================

def render_status_badge(status):
    status_text = str(status or "Unknown").strip()

    styles = {
        "pending": ("#FFF3CD", "#856404"),
        "confirmed": ("#D4EDDA", "#155724"),
        "completed": ("#D1ECF1", "#0C5460"),
        "cancelled": ("#F8D7DA", "#721C24"),
        "canceled": ("#F8D7DA", "#721C24"),
        "rejected": ("#F8D7DA", "#721C24"),
    }

    background, color = styles.get(
        status_text.lower(),
        ("#E2E3E5", "#383D41"),
    )

    safe_status = html.escape(status_text)

    st.markdown(
        f'<span style="display:inline-block;'
        f'padding:4px 12px;'
        f'border-radius:16px;'
        f'font-weight:600;'
        f'font-size:13px;'
        f'background:{background};'
        f'color:{color};">'
        f'{safe_status}</span>',
        unsafe_allow_html=True,
    )


# =========================================================
# ACCESSIBILITY SETTINGS
# =========================================================

st.session_state.setdefault("large_text_mode", False)
st.session_state.setdefault("high_contrast_mode", False)

st.sidebar.subheader("♿ Accessibility")

st.sidebar.toggle(
    "🔠 Large Text Mode",
    key="large_text_mode",
)

st.sidebar.toggle(
    "⚫ High Contrast Mode",
    key="high_contrast_mode",
)

apply_accessibility()


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.divider()
    st.subheader("🏥 Smart Hospital")
    st.caption("Patient Workspace")

    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("main.py")

    if st.button("👤 Patient Dashboard", use_container_width=True):
        st.switch_page("pages/patient_dashboard.py")

    if st.button("📅 Appointments", use_container_width=True):
        st.switch_page("pages/appointments.py")

    if st.button("📋 Medical Records", use_container_width=True):
        st.switch_page("pages/patient_dashboard.py")

    if st.button("🤖 Medical AI Assistant", use_container_width=True):
        st.switch_page("pages/medical_assistant.py")

    if st.button("🚨 Emergency Assessment", use_container_width=True):
        st.switch_page("pages/emergency.py")

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")


# =========================================================
# PAGE HEADER
# =========================================================

st.title(f"👤 {get_text(language, 'dashboard')}")
st.info(f"🌐 {get_text(language, 'welcome')}")


# =========================================================
# VOICE COMMANDS
# =========================================================

st.subheader("🎙️ Voice Commands")

st.write(
    "Speak a command to find a section of the Patient Dashboard."
)

voice_command = speech_to_text(
    start_prompt="🎤 Speak a Command",
    stop_prompt="⏹️ Stop Recording",
    language="en",
    use_container_width=True,
    key="dashboard_voice_command_input",
)

if isinstance(voice_command, str) and voice_command.strip():
    st.session_state["recognized_dashboard_command"] = (
        voice_command.strip()
    )

command = st.session_state.get("recognized_dashboard_command", "")

if command:
    st.info(f"Recognized command: {command}")

    normalized_command = command.lower().strip()

    command_messages = {
        "medicine": "💊 Find the Medicine Information section below.",
        "symptom": "🩺 Find the Symptom Checker section below.",
        "assistant": "🤖 Find the Medical AI Assistant section below.",
        "ai results": "🤖 Find the Medical AI Assistant section below.",
        "appointment": "📅 Find the Appointments section below.",
        "medical record": "📁 Find the Medical Records section below.",
        "health assessment": "❤️ Find the Latest Health Assessment section below.",
    }

    matching_message = next(
        (
            message
            for keyword, message in command_messages.items()
            if keyword in normalized_command
        ),
        None,
    )

    if matching_message:
        st.success(matching_message)
    else:
        st.warning(
            "Command not recognized. Try: medicine, symptom checker, "
            "AI assistant, appointments, medical records, or health assessment."
        )

    if st.button("🗑️ Clear Voice Command"):
        st.session_state["recognized_dashboard_command"] = ""
        st.rerun()

st.divider()


# =========================================================
# LOGIN CHECK
# =========================================================

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.stop()

token = st.session_state.get("access_token")
user_id = st.session_state.get("user_id")

if not token or not user_id:
    st.error("Login information is missing. Please login again.")
    st.stop()

headers = {
    "Authorization": f"Bearer {token}"
}


# =========================================================
# FETCH PATIENT DASHBOARD
# =========================================================

patient = {}
health = {}

try:
    dashboard_response = requests.get(
        f"{API_URL}/patients/dashboard/{user_id}",
        headers=headers,
        timeout=15,
    )

    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json()

        patient = dashboard_data.get("patient") or {}

        health = (
            dashboard_data.get("health")
            or dashboard_data.get("latest_health_assessment")
            or {}
        )

    elif dashboard_response.status_code == 401:
        st.error("Your session has expired. Please log in again.")
        st.stop()

    elif dashboard_response.status_code == 404:
        st.warning("Patient profile not found for this account.")
        st.stop()

    else:
        try:
            detail = dashboard_response.json().get(
                "detail",
                "Unable to load patient dashboard.",
            )
        except (ValueError, AttributeError):
            detail = "Unable to load patient dashboard."

        st.error(
            f"Dashboard request failed "
            f"(HTTP {dashboard_response.status_code}): {detail}"
        )
        st.stop()

except requests.exceptions.Timeout:
    st.error("The patient dashboard request timed out. Please try again.")
    st.stop()

except requests.exceptions.RequestException as error:
    st.error(f"Dashboard request failed: {error}")
    st.stop()

except ValueError:
    st.error("The backend returned an invalid JSON response.")
    st.stop()


# =========================================================
# PATIENT PROFILE
# =========================================================

st.subheader("👤 Patient Profile")

if patient:
    profile_cols = st.columns(3)

    with profile_cols[0]:
        st.write(
            "**Name:**",
            patient.get("full_name")
            or patient.get("name")
            or patient.get("patient_name")
            or "N/A",
        )

    with profile_cols[1]:
        st.write("**Email:**", patient.get("email", "N/A"))

    with profile_cols[2]:
        st.write(
            "**Phone:**",
            patient.get("phone")
            or patient.get("phone_number")
            or "N/A",
        )
else:
    st.info(
        "Patient profile details are not available "
        "in the dashboard response."
    )

st.divider()


# =========================================================
# LATEST HEALTH ASSESSMENT
# =========================================================

st.subheader("🩺 Latest Health Assessment")

if health:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "❤️ Heart Rate",
            f"{health.get('heart_rate', 'N/A')} BPM",
        )

    with col2:
        st.metric(
            "🩸 Blood Pressure",
            f"{health.get('systolic_bp', 'N/A')}/"
            f"{health.get('diastolic_bp', 'N/A')}",
        )

    with col3:
        st.metric(
            "🫁 SpO₂",
            f"{health.get('oxygen_level', 'N/A')}%",
        )

    with col4:
        st.metric(
            "⚠️ Risk Score",
            health.get("risk_score", "N/A"),
        )

    st.write(
        "**Emergency Level:**",
        health.get("emergency_level", "N/A"),
    )

    st.write(
        "**Temperature:**",
        health.get("temperature", "N/A"),
    )

    st.write(
        "**Symptoms:**",
        health.get("symptoms", "N/A"),
    )

    st.write(
        "**Recommendation:**",
        health.get(
            "ai_recommendation",
            "No recommendation available.",
        ),
    )

    st.caption(
        f"Assessment Date: "
        f"{health.get('assessment_date', 'N/A')}"
    )

else:
    st.info(
        "No health assessment found. "
        "Please complete an emergency health assessment first."
    )

st.divider()


# =========================================================
# APPOINTMENT BOOKING
# =========================================================

st.subheader(f"📅 {get_text(language, 'my_appointments')}")
st.markdown("### 📝 Book a New Appointment")

with st.container(border=True):
    st.write(
        "Enter your appointment details below. "
        "Your booking will be saved in the existing system."
    )

    with st.form("patient_book_appointment_form"):
        doctor_id = st.number_input(
            "Doctor ID",
            min_value=1,
            value=1,
            step=1,
        )

        date_col, time_col = st.columns(2)

        with date_col:
            appointment_date = st.date_input(
                "Appointment Date",
                value=date.today(),
                min_value=date.today(),
            )

        with time_col:
            appointment_time = st.time_input(
                "Appointment Time",
                value=time(10, 0),
            )

        reason = st.text_area(
            "Reason for Appointment",
            placeholder=(
                "Example: routine check-up, fever, headache..."
            ),
            max_chars=500,
        )

        submitted = st.form_submit_button(
            "📅 Book Appointment",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        if not reason.strip():
            st.warning(
                "Please enter the reason for your appointment."
            )

        else:
            payload = {
                "user_id": int(user_id),
                "doctor_id": int(doctor_id),
                "appointment_date": appointment_date.strftime(
                    "%Y-%m-%d"
                ),
                "appointment_time": appointment_time.strftime(
                    "%H:%M"
                ),
                "reason": reason.strip(),
            }

            try:
                booking_response = requests.post(
                    f"{API_URL}/appointments/book",
                    headers=headers,
                    json=payload,
                    timeout=15,
                )

                if booking_response.status_code in (200, 201):
                    try:
                        booking_data = booking_response.json()
                    except ValueError:
                        booking_data = {}

                    st.success(
                        "Appointment booked successfully! "
                        "Your appointment is awaiting confirmation."
                    )

                    st.write(
                        "**Appointment ID:**",
                        booking_data.get("appointment_id", "N/A"),
                    )

                    doctor = booking_data.get("doctor") or {}
                    hospital = booking_data.get("hospital") or {}

                    st.write(
                        "**Doctor:**",
                        doctor.get("doctor_name", "N/A"),
                    )

                    st.write(
                        "**Specialization:**",
                        doctor.get("specialization", "N/A"),
                    )

                    st.write(
                        "**Hospital:**",
                        hospital.get("hospital_name", "N/A"),
                    )

                    st.write(
                        "**Date:**",
                        booking_data.get(
                            "appointment_date",
                            payload["appointment_date"],
                        ),
                    )

                    st.write(
                        "**Time:**",
                        booking_data.get(
                            "appointment_time",
                            payload["appointment_time"],
                        ),
                    )

                    st.write(
                        "**Status:**",
                        booking_data.get("status", "Pending"),
                    )

                elif booking_response.status_code == 401:
                    st.error(
                        "Your session has expired. Please log in again."
                    )

                else:
                    try:
                        error_message = booking_response.json().get(
                            "detail",
                            "Unable to book the appointment.",
                        )
                    except (ValueError, AttributeError):
                        error_message = (
                            "Unable to book the appointment."
                        )

                    st.error(f"Booking failed: {error_message}")

            except requests.exceptions.RequestException as error:
                st.error(
                    "Could not connect to the backend. "
                    "Please check that FastAPI is running. "
                    f"Details: {error}"
                )

st.divider()


# =========================================================
# FETCH, FILTER, DISPLAY, AND CANCEL APPOINTMENTS
# =========================================================

try:
    appointment_response = requests.get(
        f"{API_URL}/appointments/patient/{user_id}",
        headers=headers,
        timeout=15,
    )

    if appointment_response.status_code == 200:
        appointment_data = appointment_response.json()
        appointments = appointment_data.get("appointments", []) or []

        # -------------------------------------------------
        # SEARCH AND FILTER
        # -------------------------------------------------

        st.markdown("### 🔎 Find an Appointment")

        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:
            appointment_search = st.text_input(
                "Search by doctor or reason",
                placeholder="Enter doctor name or reason...",
                key="patient_appointment_search",
            )

        with filter_col2:
            appointment_status_filter = st.selectbox(
                "Filter by status",
                [
                    "All",
                    "Pending",
                    "Confirmed",
                    "Completed",
                    "Cancelled",
                    "Rejected",
                ],
                key="patient_appointment_status_filter",
            )

        filtered_appointments = []
        search_text = appointment_search.strip().lower()

        for item in appointments:
            doctor_info = item.get("doctor") or {}

            doctor_name = str(
                doctor_info.get("doctor_name") or ""
            )

            reason_text = str(item.get("reason") or "")
            status_text = str(item.get("status") or "")

            matches_search = (
                not search_text
                or search_text in doctor_name.lower()
                or search_text in reason_text.lower()
            )

            matches_status = (
                appointment_status_filter == "All"
                or status_text.lower()
                == appointment_status_filter.lower()
                or (
                    appointment_status_filter == "Cancelled"
                    and status_text.lower() == "canceled"
                )
            )

            if matches_search and matches_status:
                filtered_appointments.append(item)

        st.caption(
            f"Showing {len(filtered_appointments)} of "
            f"{len(appointments)} appointments"
        )

        # -------------------------------------------------
        # UPCOMING APPOINTMENTS
        # -------------------------------------------------

        st.markdown("### 📅 Upcoming Appointments")

        upcoming_appointments = []

        for item in appointments:
            status_lower = str(
                item.get("status") or ""
            ).strip().lower()

            if status_lower in {
                "cancelled",
                "canceled",
                "rejected",
                "completed",
            }:
                continue

            raw_date = str(
                item.get("appointment_date") or ""
            ).strip()

            try:
                appointment_day = date.fromisoformat(raw_date[:10])
            except (ValueError, TypeError):
                continue

            if appointment_day >= date.today():
                upcoming_appointments.append(item)

        upcoming_appointments.sort(
            key=lambda item: (
                str(item.get("appointment_date") or ""),
                str(item.get("appointment_time") or ""),
            )
        )

        if upcoming_appointments:
            st.caption(
                f"{len(upcoming_appointments)} upcoming appointment(s)"
            )

            for item in upcoming_appointments:
                doctor_info = item.get("doctor") or {}
                hospital_info = item.get("hospital") or {}

                with st.container(border=True):
                    upcoming_col1, upcoming_col2 = st.columns([3, 1])

                    with upcoming_col1:
                        st.markdown(
                            f"**Appointment "
                            f"#{item.get('appointment_id', 'N/A')}**"
                        )

                        st.write(
                            "👨‍⚕️ Doctor:",
                            doctor_info.get("doctor_name", "N/A"),
                        )

                        st.write(
                            "🏥 Hospital:",
                            hospital_info.get("hospital_name", "N/A"),
                        )

                        st.write(
                            "📆 Date:",
                            item.get("appointment_date", "N/A"),
                        )

                        st.write(
                            "🕒 Time:",
                            item.get("appointment_time", "N/A"),
                        )

                    with upcoming_col2:
                        st.caption("Status")
                        render_status_badge(
                            item.get("status", "Unknown")
                        )

        else:
            st.info("You have no upcoming appointments.")

        st.divider()

        # -------------------------------------------------
        # ALL APPOINTMENTS AND CANCELLATION
        # -------------------------------------------------

        st.markdown("### 📋 All Appointments")

        if not appointments:
            st.info("No appointments found.")

        elif not filtered_appointments:
            st.info(
                "No appointments match your search "
                "or selected status."
            )

        else:
            st.success(
                f"Total Appointments: {len(appointments)}"
            )

            for appointment in filtered_appointments:
                appointment_id = appointment.get("appointment_id")
                status = appointment.get("status", "N/A")

                display_id = (
                    appointment_id
                    if appointment_id is not None
                    else "N/A"
                )

                with st.expander(
                    f"Appointment #{display_id} — {status}"
                ):
                    doctor = appointment.get("doctor") or {}
                    hospital = appointment.get("hospital") or {}

                    st.write("### 👨‍⚕️ Doctor Information")

                    st.write(
                        "**Doctor:**",
                        doctor.get("doctor_name", "N/A"),
                    )

                    st.write(
                        "**Specialization:**",
                        doctor.get("specialization", "N/A"),
                    )

                    st.write(
                        "**Qualification:**",
                        doctor.get("qualification", "N/A"),
                    )

                    st.write(
                        "**Experience:**",
                        doctor.get("experience", "N/A"),
                    )

                    st.write("### 🏥 Hospital Information")

                    st.write(
                        "**Hospital:**",
                        hospital.get("hospital_name", "N/A"),
                    )

                    st.write("### 📅 Appointment Details")

                    st.write(
                        "**Date:**",
                        appointment.get("appointment_date", "N/A"),
                    )

                    st.write(
                        "**Time:**",
                        appointment.get("appointment_time", "N/A"),
                    )

                    st.write(
                        "**Reason:**",
                        appointment.get("reason", "N/A"),
                    )

                    st.write("**Status:**")
                    render_status_badge(status)

                    notes = appointment.get("notes")

                    if notes:
                        st.write("**Doctor Notes:**", notes)

                    # -------------------------------------
                    # CANCEL APPOINTMENT
                    # -------------------------------------

                    status_lower = str(
                        status or ""
                    ).strip().lower()

                    if (
                        status_lower in {"pending", "confirmed"}
                        and appointment_id is not None
                    ):
                        confirm_key = (
                            f"confirm_cancel_{appointment_id}"
                        )

                        if st.button(
                            "❌ Cancel Appointment",
                            key=f"cancel_btn_{appointment_id}",
                        ):
                            st.session_state[confirm_key] = True

                        if st.session_state.get(confirm_key, False):
                            st.warning(
                                "Are you sure you want to cancel "
                                "this appointment?"
                            )

                            confirm_col, keep_col = st.columns(2)

                            with confirm_col:
                                if st.button(
                                    "Yes, Cancel",
                                    key=f"confirm_yes_{appointment_id}",
                                    type="primary",
                                ):
                                    try:
                                        cancel_response = requests.put(
                                            f"{API_URL}/appointments/"
                                            f"{appointment_id}/status",
                                            headers=headers,
                                            json={"status": "Cancelled"},
                                            timeout=15,
                                        )

                                        if cancel_response.status_code == 200:
                                            st.session_state[
                                                confirm_key
                                            ] = False

                                            st.success(
                                                "Appointment cancelled successfully."
                                            )
                                            st.rerun()

                                        else:
                                            try:
                                                cancel_detail = (
                                                    cancel_response.json().get(
                                                        "detail",
                                                        cancel_response.text,
                                                    )
                                                )
                                            except (
                                                ValueError,
                                                AttributeError,
                                            ):
                                                cancel_detail = (
                                                    cancel_response.text
                                                )

                                            st.error(
                                                "Cancellation failed "
                                                f"(HTTP {cancel_response.status_code}): "
                                                f"{cancel_detail}"
                                            )

                                    except requests.exceptions.RequestException as error:
                                        st.error(
                                            "Could not connect to the backend: "
                                            f"{error}"
                                        )

                            with keep_col:
                                if st.button(
                                    "Keep Appointment",
                                    key=f"confirm_no_{appointment_id}",
                                ):
                                    st.session_state[
                                        confirm_key
                                    ] = False
                                    st.rerun()

                    elif status_lower in {"cancelled", "canceled"}:
                        st.info(
                            "This appointment has been cancelled."
                        )

    elif appointment_response.status_code == 401:
        st.error(
            "Your login session has expired. Please log in again."
        )

    else:
        st.error(
            "Unable to load appointments "
            f"(HTTP {appointment_response.status_code})."
        )

except requests.exceptions.RequestException as error:
    st.error(f"Appointment request failed: {error}")

except ValueError:
    st.error("The backend returned invalid appointment data.")

st.divider()


# =========================================================
# MEDICAL RECORDS
# =========================================================

st.subheader(f"📁 {get_text(language, 'medical_records')}")

patient_id = patient.get("patient_id")

if not patient_id:
    st.info("Patient ID not available.")

else:
    try:
        records_response = requests.get(
            f"{API_URL}/medical-records/patient/{patient_id}",
            headers=headers,
            timeout=15,
        )

        if records_response.status_code == 200:
            records_data = records_response.json()
            records = records_data.get("records", []) or []

            if not records:
                st.info("No medical records found.")

            else:
                st.success(
                    f"Total Medical Records: {len(records)}"
                )

                for record in records:
                    record_id = record.get("record_id", "N/A")

                    with st.expander(f"📋 Record #{record_id}"):
                        st.write(
                            "**Date:**",
                            record.get("record_date", "N/A"),
                        )

                        st.write(
                            "**Symptoms:**",
                            record.get("symptoms", "N/A"),
                        )

                        st.write(
                            "**Diagnosis:**",
                            record.get("diagnosis", "N/A"),
                        )

                        st.write(
                            "**Allergies:**",
                            record.get("allergies", "N/A"),
                        )

                        st.write(
                            "**Existing Conditions:**",
                            record.get("existing_conditions", "N/A"),
                        )

                        st.write(
                            "**Doctor Notes:**",
                            record.get("doctor_notes", "N/A"),
                        )

        elif records_response.status_code == 401:
            st.error(
                "Your login session has expired. Please log in again."
            )

        else:
            st.error(
                "Unable to load medical records "
                f"(HTTP {records_response.status_code})."
            )

    except requests.exceptions.RequestException as error:
        st.error(f"Medical records request failed: {error}")

    except ValueError:
        st.error("The backend returned invalid medical-record data.")

st.divider()


# =========================================================
# SYMPTOM CHECKER WITH VOICE INPUT
# =========================================================

st.subheader("🩺 Symptom Checker")

st.write(
    "Enter your symptom by typing or using your voice."
)

add_speaker_button(
    "Welcome to the Symptom Checker. You can type your symptoms "
    "or use the microphone to speak your symptoms. Then select "
    "Check Symptom to view available information. This information "
    "is educational and does not replace advice from a qualified "
    "healthcare professional.",
    "🔊 Read Symptom Checker Instructions",
    speech_language,
)

voice_text = speech_to_text(
    start_prompt="🎤 Speak Symptoms",
    stop_prompt="⏹️ Stop Recording",
    language="en",
    use_container_width=True,
    key="symptom_voice_input",
)

if voice_text:
    st.session_state["voice_symptom_text"] = voice_text

st.session_state.setdefault("voice_symptom_text", "")

symptom = st.text_input(
    "Enter your symptom",
    placeholder="e.g. fever, allergy, headache",
    key="symptom_text_input",
)

if st.session_state["voice_symptom_text"]:
    st.info(
        f"Voice input: {st.session_state['voice_symptom_text']}"
    )

    if st.button("🗑️ Clear Voice Input"):
        st.session_state["voice_symptom_text"] = ""
        st.rerun()

if st.button("🔍 Check Symptom", use_container_width=True):
    selected_symptom = (
        symptom.strip()
        or st.session_state["voice_symptom_text"].strip()
    )

    if not selected_symptom:
        st.warning("Please type or speak a symptom.")

    else:
        try:
            encoded_symptom = quote(
                selected_symptom,
                safe="",
            )

            symptom_response = requests.get(
                f"{API_URL}/symptoms/search/{encoded_symptom}",
                headers=headers,
                timeout=15,
            )

            if symptom_response.status_code == 200:
                symptom_data = symptom_response.json()

                st.info(
                    f"Information for: "
                    f"{symptom_data.get('symptom', selected_symptom)}"
                )

                results = symptom_data.get("results", []) or []

                if not results:
                    st.info(
                        "No matching information was found."
                    )

                for result in results:
                    with st.expander(
                        f"💊 {result.get('medicine_name', 'N/A')}"
                    ):
                        possible_condition = result.get(
                            "possible_condition",
                            "N/A",
                        )

                        medicine_use = result.get(
                            "medicine_use",
                            "N/A",
                        )

                        precautions_text = result.get(
                            "precautions",
                            "N/A",
                        )

                        doctor_advice = result.get(
                            "when_to_see_doctor",
                            "N/A",
                        )

                        st.write(
                            "**Possible Condition:**",
                            possible_condition,
                        )

                        st.write(
                            "**Medicine Use:**",
                            medicine_use,
                        )

                        st.write(
                            "**Precautions:**",
                            precautions_text,
                        )

                        st.warning(
                            f"**When to see a doctor:** "
                            f"{doctor_advice}"
                        )

                        add_speaker_button(
                            f"Possible condition: {possible_condition}. "
                            f"Medicine use: {medicine_use}. "
                            f"Precautions: {precautions_text}. "
                            f"When to see a doctor: {doctor_advice}.",
                            "🔊 Listen to Symptom Information",
                            speech_language,
                        )

                st.caption(symptom_data.get("notice", ""))

            elif symptom_response.status_code == 404:
                st.info(
                    "No information found for this symptom."
                )

            elif symptom_response.status_code == 401:
                st.error(
                    "Your login session has expired. Please log in again."
                )

            else:
                st.error(
                    "Unable to check symptom "
                    f"(HTTP {symptom_response.status_code})."
                )

        except requests.exceptions.RequestException as error:
            st.error(f"Symptom request failed: {error}")

        except ValueError:
            st.error("The backend returned invalid symptom data.")

st.divider()


# =========================================================
# MEDICINE INFORMATION
# =========================================================

st.subheader(f"💊 {get_text(language, 'medicines')}")

medicine_name = st.text_input(
    "Search Medicine",
    placeholder="Enter medicine name, e.g. Paracetamol",
    key="medicine_search_input",
)

if st.button("🔍 Search Medicine", use_container_width=True):
    if not medicine_name.strip():
        st.warning("Please enter a medicine name.")

    else:
        try:
            encoded_medicine = quote(
                medicine_name.strip(),
                safe="",
            )

            medicine_response = requests.get(
                f"{API_URL}/medicines/search/{encoded_medicine}",
                headers=headers,
                timeout=15,
            )

            if medicine_response.status_code == 200:
                medicine_data = medicine_response.json()
                medicines = medicine_data.get("results", []) or []

                if not medicines:
                    st.info("No medicine found.")

                for medicine in medicines:
                    with st.expander(
                        f"💊 {medicine.get('medicine_name', 'N/A')}"
                    ):
                        generic_name = medicine.get(
                            "generic_name",
                            "N/A",
                        )

                        category = medicine.get("category", "N/A")
                        uses = medicine.get("uses", "N/A")

                        precautions = medicine.get(
                            "precautions",
                            "N/A",
                        )

                        side_effects = medicine.get(
                            "side_effects",
                            "N/A",
                        )

                        prescription = medicine.get(
                            "prescription_required",
                            "N/A",
                        )

                        doctor_verified = medicine.get(
                            "doctor_verified",
                            "N/A",
                        )

                        st.write(
                            "**Generic Name:**",
                            generic_name,
                        )

                        st.write("**Category:**", category)
                        st.write("**Uses:**", uses)
                        st.write("**Precautions:**", precautions)

                        st.write(
                            "**Possible Side Effects:**",
                            side_effects,
                        )

                        st.write(
                            "**Prescription Required:**",
                            prescription,
                        )

                        st.write(
                            "**Doctor Verified:**",
                            doctor_verified,
                        )

                        st.warning(
                            "Medicine information is for educational "
                            "purposes only. Consult a qualified healthcare "
                            "professional before using or changing any medicine."
                        )

                        medicine_speech = (
                            f"Medicine name: "
                            f"{medicine.get('medicine_name', 'N/A')}. "
                            f"Generic name: {generic_name}. "
                            f"Category: {category}. "
                            f"Uses: {uses}. "
                            f"Precautions: {precautions}. "
                            f"Possible side effects: {side_effects}. "
                            f"Prescription required: {prescription}. "
                            f"Doctor verified: {doctor_verified}. "
                            "Please consult a qualified healthcare "
                            "professional before using this medicine."
                        )

                        add_speaker_button(
                            medicine_speech,
                            "🔊 Listen to Medicine Details",
                            speech_language,
                        )

            elif medicine_response.status_code == 401:
                st.error(
                    "Your login session has expired. Please log in again."
                )

            elif medicine_response.status_code == 404:
                st.info("Medicine not found.")

            else:
                st.error(
                    "Unable to search medicine "
                    f"(HTTP {medicine_response.status_code})."
                )

        except requests.exceptions.RequestException as error:
            st.error(f"Medicine search failed: {error}")

        except ValueError:
            st.error("The backend returned invalid medicine data.")

st.divider()


# =========================================================
# MEDICAL AI ASSISTANT
# =========================================================

st.subheader(f"🤖 {get_text(language, 'ai_assistant')}")

st.write(
    "Enter your symptoms to get an educational disease prediction "
    "and related information."
)

symptoms_input = st.text_input(
    "Enter symptoms separated by comma",
    placeholder="e.g. fever, headache, fatigue",
    key="ai_symptoms_input",
)

if st.button("🤖 Analyze Symptoms", use_container_width=True):
    if not symptoms_input.strip():
        st.warning("Please enter at least one symptom.")

    else:
        symptoms = [
            item.strip()
            for item in symptoms_input.split(",")
            if item.strip()
        ]

        try:
            ai_response = requests.post(
                f"{API_URL}/disease-assistant/analyze",
                json={
                    "symptoms": symptoms,
                    "language": language,
                },
                headers=headers,
                timeout=60,
            )

            if ai_response.status_code == 200:
                ai_data = ai_response.json()

                st.success("Disease analysis completed.")

                confidence = ai_data.get("confidence")

                predicted_disease = ai_data.get(
                    "predicted_disease",
                    "N/A",
                )

                if confidence is not None:
                    try:
                        confidence_value = float(confidence)
                        confidence_percent = confidence_value * 100

                        if confidence_value < 0.50:
                            st.warning(
                                "⚠️ The AI could not determine the "
                                "condition reliably from the supplied symptoms."
                            )

                        st.write(
                            "**Prediction Confidence:**",
                            f"{confidence_percent:.2f}%",
                        )

                    except (TypeError, ValueError):
                        confidence_percent = None

                        st.write(
                            "**Prediction Confidence:**",
                            confidence,
                        )
                else:
                    confidence_percent = None

                st.write(
                    "**Predicted Disease:**",
                    predicted_disease,
                )

                matched_symptoms = (
                    ai_data.get("matched_symptoms", []) or []
                )

                st.write(
                    "**Matched Symptoms:**",
                    ", ".join(map(str, matched_symptoms)),
                )

                description = ai_data.get("description", "")

                if description:
                    st.write("**Description:**")
                    st.info(description)

                precautions = ai_data.get("precautions", []) or []

                if precautions:
                    st.write("**Precautions:**")

                    for precaution in precautions:
                        st.write(f"• {precaution}")

                ai_notice = ai_data.get(
                    "notice",
                    "This information is for educational purposes only.",
                )

                st.warning(ai_notice)

                speech_parts = [
                    "Medical AI Assistant results. "
                    f"Predicted condition: {predicted_disease}."
                ]

                if confidence_percent is not None:
                    speech_parts.append(
                        f"Prediction confidence: "
                        f"{confidence_percent:.2f} percent."
                    )

                if matched_symptoms:
                    speech_parts.append(
                        "Matched symptoms: "
                        + ", ".join(map(str, matched_symptoms))
                        + "."
                    )

                if description:
                    speech_parts.append(
                        "Description: " + str(description)
                    )

                if precautions:
                    speech_parts.append(
                        "Precautions: "
                        + ". ".join(map(str, precautions))
                    )

                speech_parts.append(str(ai_notice))

                add_speaker_button(
                    " ".join(speech_parts),
                    "🔊 Listen to AI Response",
                    speech_language,
                )

            elif ai_response.status_code == 400:
                try:
                    st.error(
                        ai_response.json().get(
                            "detail",
                            "Unsupported symptoms.",
                        )
                    )
                except (ValueError, AttributeError):
                    st.error("Unsupported symptoms.")

            elif ai_response.status_code == 401:
                st.error(
                    "Your login session has expired. Please log in again."
                )

            else:
                try:
                    st.error(
                        ai_response.json().get(
                            "detail",
                            "Unable to analyze symptoms.",
                        )
                    )
                except (ValueError, AttributeError):
                    st.error(
                        "Unable to analyze symptoms "
                        f"(HTTP {ai_response.status_code})."
                    )

        except requests.exceptions.RequestException as error:
            st.error(f"AI analysis failed: {error}")

        except ValueError:
            st.error("The backend returned invalid AI analysis data.")

st.divider()


# =========================================================
# DISEASE PREDICTION HISTORY
# =========================================================

st.subheader("📊 Disease Prediction History")

patient_id = patient.get("patient_id")

if not patient_id:
    st.info("Patient ID is not available.")

else:
    try:
        history_response = requests.get(
            f"{API_URL}/predictions/{patient_id}",
            headers=headers,
            timeout=15,
        )

        if history_response.status_code == 200:
            history_data = history_response.json()

            predictions = (
                history_data.get("predictions", []) or []
            )

            st.metric(
                "Total Saved Predictions",
                history_data.get(
                    "total_predictions",
                    len(predictions),
                ),
            )

            if predictions:
                import pandas as pd

                prediction_rows = []

                for record in predictions:
                    confidence = record.get("confidence_score")

                    if confidence not in (None, ""):
                        try:
                            confidence = (
                                f"{float(confidence) * 100:.2f}%"
                            )
                        except (TypeError, ValueError):
                            confidence = str(confidence)
                    else:
                        confidence = "N/A"

                    prediction_rows.append(
                        {
                            "Prediction ID": record.get(
                                "prediction_id",
                                "N/A",
                            ),
                            "Date": record.get(
                                "prediction_date",
                                "N/A",
                            ),
                            "Predicted Disease": record.get(
                                "predicted_result",
                                "N/A",
                            ),
                            "Confidence Score": confidence,
                            "Model": record.get(
                                "model_name",
                                "N/A",
                            ),
                            "Symptoms / Details": record.get(
                                "explanation",
                                "N/A",
                            ),
                        }
                    )

                st.dataframe(
                    pd.DataFrame(prediction_rows),
                    use_container_width=True,
                    hide_index=True,
                )

                st.caption(
                    "Model confidence is not a clinically validated "
                    "probability or a medical diagnosis."
                )

            else:
                st.info(
                    "No saved disease predictions are available yet."
                )

        elif history_response.status_code == 401:
            st.error(
                "Your login session has expired. Please log in again."
            )

        elif history_response.status_code == 404:
            st.info(
                "No patient profile or prediction history was found."
            )

        else:
            st.error(
                "Could not load prediction history "
                f"(HTTP {history_response.status_code})."
            )

    except requests.exceptions.RequestException as error:
        st.error(f"Prediction history request failed: {error}")

    except ValueError:
        st.error("The backend returned invalid prediction-history data.")


# =========================================================
# AVAILABLE HOSPITAL MODULES
# =========================================================

st.subheader("📋 Hospital Assistant Modules")

st.info(
    "Review the available hospital services below. "
    "Use the sections above to access their current features."
)

modules = [
    (
        "🩺 Health Assessment",
        "Review your latest health assessment.",
    ),
    (
        "📊 Risk Prediction",
        "Review the risk information from your assessment.",
    ),
    (
        "📅 Appointments",
        "View your appointments and doctor details.",
    ),
    (
        "📁 Medical Records",
        "Review your available medical records.",
    ),
    (
        "💊 Medicine Information",
        "Search for medicine information.",
    ),
]

for module_name, module_description in modules:
    with st.container(border=True):
        st.markdown(f"### {module_name}")
        st.write(module_description)
        st.caption("Available")