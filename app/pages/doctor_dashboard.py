
import streamlit as st
import requests
import pandas as pd
from html import escape
from theme import apply_hospital_theme

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Doctor Dashboard - Smart Hospital",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_hospital_theme()

API_URL = "http://127.0.0.1:8001"
TIMEOUT = 15

# =====================================================
# AUTHENTICATION
# =====================================================

if not st.session_state.get("logged_in", False):
    st.warning("Please log in first.")
    st.stop()

token = st.session_state.get("access_token")
role = str(st.session_state.get("role", "")).lower()

if not token:
    st.error("Your login session is incomplete. Please log in again.")
    st.stop()

if role != "doctor":
    st.error("This dashboard is available only for doctor accounts.")
    st.stop()

headers = {"Authorization": f"Bearer {token}"}
doctor_name = str(st.session_state.get("name", "Doctor"))

# =====================================================
# HEADER
# =====================================================

st.markdown(
    """
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:18px;">
        <div style="background:#1769aa;color:white;border-radius:12px;
                    padding:10px 14px;font-size:26px;">🏥</div>
        <div>
            <div style="color:#16385f;font-size:25px;font-weight:800;">
                Smart Hospital
            </div>
            <div style="color:#71859a;font-size:12px;">
                DOCTOR WORKSPACE
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("👨‍⚕️ Doctor Dashboard")

st.markdown(
    f"""
    <div class="welcome-panel">
        <div style="font-size:20px;font-weight:750;color:#16385f;">
            Welcome, Dr. {escape(doctor_name)}!
        </div>
        <div style="color:#71859a;font-size:13px;margin-top:5px;">
            Manage appointments, review patient records, and update appointment status.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =====================================================
# DOCTOR ID
# =====================================================

doctor_id = st.number_input(
    "Doctor ID",
    min_value=1,
    value=int(st.session_state.get("doctor_id", 1)),
    step=1,
    key="doctor_dashboard_id",
)

# =====================================================
# STATUS BADGE
# =====================================================

def show_status_badge(status):
    status = str(status or "Unknown").strip()

    colors = {
        "pending": ("#fff4d6", "#8a5a00"),
        "confirmed": ("#dff7e8", "#176b3a"),
        "completed": ("#dcecff", "#174f91"),
        "cancelled": ("#f0e7ff", "#6639a6"),
        "rejected": ("#ffe4e4", "#a32121"),
    }

    background, foreground = colors.get(
        status.lower(), ("#edf1f5", "#405266")
    )

    st.markdown(
        f'<span style="display:inline-block;padding:5px 12px;'
        f'border-radius:20px;background:{background};color:{foreground};'
        f'font-weight:700;font-size:12px;">{escape(status)}</span>',
        unsafe_allow_html=True,
    )


# =====================================================
# UPDATE APPOINTMENT STATUS
# =====================================================

def update_status(appointment_id, new_status):
    if str(appointment_id) == "N/A":
        st.error("Appointment ID is missing.")
        return

    try:
        response = requests.put(
            f"{API_URL}/appointments/{appointment_id}/status",
            headers=headers,
            json={"status": new_status},
            timeout=TIMEOUT,
        )

        if response.status_code == 200:
            st.success(
                f"Appointment #{appointment_id} updated to {new_status}."
            )
            st.rerun()

        elif response.status_code == 401:
            st.error("Your session has expired. Please log in again.")

        else:
            try:
                detail = response.json().get(
                    "detail", "Unable to update appointment."
                )
            except (ValueError, AttributeError):
                detail = "Unable to update appointment."

            st.error(f"Update failed: {detail}")

    except requests.exceptions.RequestException as exc:
        st.error(f"Unable to contact the backend: {exc}")


# =====================================================
# VIEW AND UPDATE PATIENT MEDICAL RECORDS
# =====================================================

def show_medical_records(patient_id):
    if not patient_id:
        st.warning("Patient ID is not available.")
        return

    try:
        response = requests.get(
            f"{API_URL}/medical-records/patient/{patient_id}",
            headers=headers,
            timeout=TIMEOUT,
        )

        if response.status_code == 401:
            st.error("Your login session has expired. Please log in again.")
            return

        if response.status_code != 200:
            st.error(
                f"Unable to fetch medical records "
                f"(HTTP {response.status_code})."
            )
            return

        data = response.json()

        if isinstance(data, list):
            records = data
        else:
            records = data.get("records", [])

        st.info(f"Medical records found: {len(records)}")

        if not records:
            st.write("No medical records found for this patient.")
            return

        for record in records:
            record_id = record.get("record_id")

            if record_id is None:
                st.warning("A medical record is missing its record ID.")
                continue

            current_notes = record.get("doctor_notes") or ""

            with st.expander(f"📋 Medical Record #{record_id}"):
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

                st.markdown("### 📝 Doctor Notes")

                notes_key = f"doctor_notes_{record_id}"

                if notes_key not in st.session_state:
                    st.session_state[notes_key] = current_notes

                st.text_area(
                    "View or edit notes",
                    key=notes_key,
                    height=120,
                )

                if st.button(
                    "💾 Save Doctor Notes",
                    key=f"save_notes_{record_id}",
                    use_container_width=True,
                ):
                    updated_notes = st.session_state[notes_key]

                    try:
                        update_response = requests.put(
                            f"{API_URL}/medical-records/{record_id}/notes",
                            headers=headers,
                            json={"doctor_notes": updated_notes},
                            timeout=TIMEOUT,
                        )

                        if update_response.status_code == 200:
                            st.success(
                                "Doctor notes saved successfully!"
                            )
                            st.rerun()

                        elif update_response.status_code == 401:
                            st.error(
                                "Your session has expired. Please log in again."
                            )

                        else:
                            try:
                                detail = update_response.json().get(
                                    "detail",
                                    "Unable to save doctor notes.",
                                )
                            except (ValueError, AttributeError):
                                detail = "Unable to save doctor notes."

                            st.error(
                                f"Save failed "
                                f"(HTTP {update_response.status_code}): "
                                f"{detail}"
                            )

                    except requests.exceptions.RequestException as exc:
                        st.error(
                            f"Unable to contact the backend: {exc}"
                        )

    except requests.exceptions.RequestException as exc:
        st.error(f"Unable to connect to the backend: {exc}")


# =====================================================
# TODAY'S APPOINTMENTS
# =====================================================

st.divider()
st.subheader("📅 Today's Appointments")

if st.button(
    "🔄 Refresh Today's Appointments",
    key="refresh_today_appointments",
):
    st.rerun()

try:
    today_response = requests.get(
        f"{API_URL}/appointments/doctor/{doctor_id}/today",
        headers=headers,
        timeout=TIMEOUT,
    )

    if today_response.status_code == 200:
        today_data = today_response.json()

        if isinstance(today_data, list):
            today_appointments = today_data
            total_today = len(today_appointments)
        else:
            today_appointments = today_data.get("appointments", [])
            total_today = today_data.get(
                "total_appointments", len(today_appointments)
            )

        st.caption(
            f"Appointments scheduled today: {total_today}"
        )

        if today_appointments:
            rows = []

            for appointment in today_appointments:
                patient = appointment.get("patient") or {}

                rows.append(
                    {
                        "Appointment ID": appointment.get(
                            "appointment_id",
                            appointment.get("id", "N/A"),
                        ),
                        "Time": appointment.get(
                            "appointment_time", "N/A"
                        ),
                        "Patient": patient.get(
                            "name",
                            appointment.get("patient_name", "N/A"),
                        ),
                        "Reason": appointment.get("reason", "N/A"),
                        "Status": appointment.get("status", "N/A"),
                    }
                )

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No appointments scheduled for today.")

    elif today_response.status_code == 401:
        st.error("Your session has expired. Please log in again.")

    else:
        st.warning(
            "Today's appointments unavailable "
            f"(HTTP {today_response.status_code})."
        )

except requests.exceptions.RequestException as exc:
    st.error(f"Unable to load today's appointments: {exc}")


# =====================================================
# ALL APPOINTMENTS
# =====================================================

st.divider()
st.subheader("🗓️ Appointment Management")

st.caption(
    "Review appointments, view patient medical records, "
    "and update appointment status."
)

if "show_all_appointments" not in st.session_state:
    st.session_state["show_all_appointments"] = False

if st.button(
    "📋 Load / Refresh All Appointments",
    key="load_all_appointments",
    use_container_width=True,
):
    st.session_state["show_all_appointments"] = True
    st.rerun()

if st.session_state["show_all_appointments"]:
    try:
        response = requests.get(
            f"{API_URL}/appointments/doctor/{doctor_id}",
            headers=headers,
            timeout=TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, list):
                appointments = data
            else:
                appointments = data.get("appointments", [])

            if not appointments:
                st.info("No appointments found.")

            else:
                for appointment in appointments:
                    appointment_id = appointment.get(
                        "appointment_id",
                        appointment.get("id", "N/A"),
                    )

                    patient = appointment.get("patient") or {}

                    patient_id = patient.get(
                        "patient_id",
                        appointment.get("patient_id"),
                    )

                    patient_name = patient.get(
                        "name",
                        appointment.get("patient_name", "Patient"),
                    )

                    status = appointment.get("status", "Pending")
                    normalized_status = str(status).strip().lower()

                    with st.expander(
                        f"📅 Appointment #{appointment_id} — "
                        f"{patient_name} — {status}"
                    ):
                        left, right = st.columns([1.2, 0.8])

                        with left:
                            st.write("**Patient:**", patient_name)
                            st.write(
                                "**Patient ID:**",
                                patient_id or "N/A",
                            )
                            st.write(
                                "**Date:**",
                                appointment.get(
                                    "appointment_date", "N/A"
                                ),
                            )
                            st.write(
                                "**Time:**",
                                appointment.get(
                                    "appointment_time", "N/A"
                                ),
                            )
                            st.write(
                                "**Reason:**",
                                appointment.get("reason", "N/A"),
                            )

                            st.write("**Status:**")
                            show_status_badge(status)

                            appointment_notes = appointment.get("notes")

                            if appointment_notes:
                                st.write(
                                    "**Notes:**",
                                    appointment_notes,
                                )

                        with right:
                            st.markdown("### ⚡ Quick Actions")

                            if st.button(
                                "📋 View Medical Records",
                                key=f"records_{appointment_id}",
                                use_container_width=True,
                            ):
                                show_medical_records(patient_id)

                            if normalized_status == "pending":
                                action_col1, action_col2 = st.columns(2)

                                with action_col1:
                                    if st.button(
                                        "✅ Confirm",
                                        key=f"confirm_{appointment_id}",
                                        use_container_width=True,
                                    ):
                                        update_status(
                                            appointment_id,
                                            "Confirmed",
                                        )

                                with action_col2:
                                    if st.button(
                                        "❌ Reject",
                                        key=f"reject_{appointment_id}",
                                        use_container_width=True,
                                    ):
                                        update_status(
                                            appointment_id,
                                            "Rejected",
                                        )

                            elif normalized_status == "confirmed":
                                if st.button(
                                    "🏁 Mark as Completed",
                                    key=f"complete_{appointment_id}",
                                    use_container_width=True,
                                ):
                                    update_status(
                                        appointment_id,
                                        "Completed",
                                    )

                            elif normalized_status == "completed":
                                st.success("✅ Appointment completed")

                            elif normalized_status == "rejected":
                                st.error("❌ Appointment rejected")

                            elif normalized_status == "cancelled":
                                st.warning("Appointment cancelled")

                            with st.expander(
                                "⚙️ Advanced: Change Status"
                            ):
                                status_options = [
                                    "Pending",
                                    "Confirmed",
                                    "Rejected",
                                    "Completed",
                                    "Cancelled",
                                ]

                                current_status = next(
                                    (
                                        option
                                        for option in status_options
                                        if option.lower()
                                        == normalized_status
                                    ),
                                    None,
                                )

                                selected_status = st.selectbox(
                                    "Appointment status",
                                    status_options,
                                    index=(
                                        status_options.index(
                                            current_status
                                        )
                                        if current_status
                                        else 0
                                    ),
                                    key=f"status_{appointment_id}",
                                )

                                if st.button(
                                    "💾 Update Status",
                                    key=f"update_{appointment_id}",
                                    use_container_width=True,
                                ):
                                    if str(appointment_id) == "N/A":
                                        st.error(
                                            "Appointment ID is missing."
                                        )

                                    elif (
                                        selected_status.lower()
                                        == normalized_status
                                    ):
                                        st.info(
                                            "The appointment already has "
                                            "this status."
                                        )

                                    else:
                                        update_status(
                                            appointment_id,
                                            selected_status,
                                        )

        elif response.status_code == 401:
            st.error(
                "Your session has expired. Please log in again."
            )

        else:
            st.error(
                "Unable to load appointments. "
                f"HTTP {response.status_code}"
            )

    except requests.exceptions.RequestException as exc:
        st.error(
            f"Unable to connect to the backend: {exc}"
        )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.markdown(
    """
    <div class="footer-text" style="text-align:center;padding:15px;">
        Smart Hospital Management System<br>
        Doctor Workspace
    </div>
    """,
    unsafe_allow_html=True,
)
