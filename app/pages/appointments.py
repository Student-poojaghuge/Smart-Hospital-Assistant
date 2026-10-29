
import streamlit as st
import requests
from datetime import date, time
from html import escape
from theme import apply_hospital_theme

API_URL = "http://127.0.0.1:8001"


# =========================================================
# PAGE CONFIGURATION AND THEME
# =========================================================

st.set_page_config(
    page_title="Appointments - Smart Hospital Assistant",
    page_icon="📅",
    layout="wide"
)

apply_hospital_theme()


# =========================================================
# HELPER: COLORED APPOINTMENT STATUS BADGE
# =========================================================

def show_status_badge(status):
    status = str(status or "N/A")

    status_styles = {
        "Pending": ("#FFF3CD", "#856404", "⏳"),
        "Confirmed": ("#D1FAE5", "#065F46", "✅"),
        "Cancelled": ("#FEE2E2", "#991B1B", "❌"),
        "Rejected": ("#FEE2E2", "#991B1B", "🚫"),
        "Completed": ("#DBEAFE", "#1E40AF", "✔️"),
    }

    bg_color, text_color, icon = status_styles.get(
        status,
        ("#E5E7EB", "#374151", "ℹ️")
    )

    safe_status = escape(status)

    st.markdown(
        f"""
        <span style="
            display: inline-block;
            background-color: {bg_color};
            color: {text_color};
            padding: 7px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            margin: 5px 0 12px 0;
        ">
            {icon} {safe_status}
        </span>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# LOGIN AND SESSION DETAILS
# =========================================================

if not st.session_state.get("logged_in", False):
    st.warning("Please log in to manage your appointments.")
    st.stop()

token = st.session_state.get("access_token")
user_id = st.session_state.get("user_id")

if not token or user_id is None:
    st.error("Your login session is incomplete. Please log in again.")
    st.stop()

headers = {
    "Authorization": f"Bearer {token}"
}


# =========================================================
# PAGE HEADER
# =========================================================

st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #17345C, #2476E8);
        padding: 24px 28px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 5px 18px rgba(20, 46, 80, 0.12);
    ">
        <h1 style="
            color: #FFFFFF !important;
            margin: 0;
            font-size: 30px;
        ">📅 Appointments</h1>
        <p style="
            color: #EAF3FF;
            margin: 8px 0 0 0;
            font-size: 15px;
        ">Book consultations and manage your appointments in one place.</p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# BOOK APPOINTMENT
# =========================================================

st.subheader("📅 Book an Appointment")

with st.container(border=True):
    st.caption("Enter your appointment details below.")

    doctor_id = st.number_input(
        "Doctor ID",
        min_value=1,
        value=1,
        step=1
    )

    col_date, col_time = st.columns(2)

    with col_date:
        appointment_date = st.date_input(
            "Appointment Date",
            min_value=date.today()
        )

    with col_time:
        appointment_time = st.time_input(
            "Appointment Time",
            value=time(10, 0)
        )

    reason = st.text_area(
        "Reason for Appointment",
        placeholder="Example: Fever, routine check-up, headache..."
    )

    book_clicked = st.button(
        "📅 Book Appointment",
        use_container_width=True,
        type="primary"
    )


if book_clicked:
    if not reason.strip():
        st.warning("Please enter the reason for appointment.")

    else:
        payload = {
            "user_id": user_id,
            "doctor_id": int(doctor_id),
            "appointment_date": appointment_date.strftime("%Y-%m-%d"),
            "appointment_time": appointment_time.strftime("%H:%M"),
            "reason": reason.strip()
        }

        try:
            response = requests.post(
                f"{API_URL}/appointments/book",
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                st.success("Appointment booked successfully! ✅")
                st.subheader("📋 Appointment Details")

                col1, col2 = st.columns(2)

                with col1:
                    st.write(
                        "**Appointment ID:**",
                        data.get("appointment_id", "N/A")
                    )

                    doctor = data.get("doctor") or {}

                    st.write(
                        "**Doctor:**",
                        doctor.get("doctor_name", "N/A")
                    )

                    st.write(
                        "**Specialization:**",
                        doctor.get("specialization", "N/A")
                    )

                    st.write(
                        "**Qualification:**",
                        doctor.get("qualification", "N/A")
                    )

                with col2:
                    hospital = data.get("hospital") or {}

                    st.write(
                        "**Hospital:**",
                        hospital.get("hospital_name", "N/A")
                    )

                    st.write(
                        "**Date:**",
                        data.get("appointment_date", "N/A")
                    )

                    st.write(
                        "**Time:**",
                        data.get("appointment_time", "N/A")
                    )

                    st.write("**Status:**")
                    show_status_badge(data.get("status", "Pending"))

            elif response.status_code == 401:
                st.error(
                    "Your login session has expired. Please log in again."
                )

            else:
                try:
                    error_data = response.json()
                    st.error(
                        error_data.get(
                            "detail",
                            "Unable to book appointment."
                        )
                    )
                except ValueError:
                    st.error("Unable to book appointment.")

        except requests.exceptions.RequestException as error:
            st.error(f"Unable to reach the backend: {error}")


st.divider()


# =========================================================
# MY APPOINTMENTS
# =========================================================

st.subheader("📋 My Appointments")

if st.button(
    "🔄 Refresh Appointments",
    use_container_width=True
):
    st.rerun()


try:
    response = requests.get(
        f"{API_URL}/appointments/patient/{user_id}",
        headers=headers,
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        appointments = data.get("appointments") or []

        # -------------------------------------------------
        # APPOINTMENT SUMMARY
        # -------------------------------------------------

        total_count = len(appointments)

        pending_count = sum(
            1 for appointment in appointments
            if appointment.get("status") == "Pending"
        )

        confirmed_count = sum(
            1 for appointment in appointments
            if appointment.get("status") == "Confirmed"
        )

        cancelled_count = sum(
            1 for appointment in appointments
            if appointment.get("status") == "Cancelled"
        )

        st.subheader("📊 Appointment Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Appointments", total_count)

        with col2:
            st.metric("⏳ Pending", pending_count)

        with col3:
            st.metric("✅ Confirmed", confirmed_count)

        with col4:
            st.metric("❌ Cancelled", cancelled_count)

        st.divider()

        # -------------------------------------------------
        # APPOINTMENT HISTORY
        # -------------------------------------------------

        if not appointments:
            st.info("No appointments found.")

        else:
            for appointment in appointments:
                doctor = appointment.get("doctor") or {}
                hospital = appointment.get("hospital") or {}

                appointment_id = appointment.get("appointment_id")
                status = appointment.get("status", "N/A")

                appointment_date_value = appointment.get(
                    "appointment_date", "Date unavailable"
                )
                appointment_time_value = appointment.get(
                    "appointment_time", "Time unavailable"
                )

                with st.expander(
                    f"Appointment #{appointment_id} — "
                    f"{appointment_date_value} "
                    f"{appointment_time_value}"
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(
                            "**Doctor:**",
                            doctor.get("doctor_name", "N/A")
                        )

                        st.write(
                            "**Specialization:**",
                            doctor.get("specialization", "N/A")
                        )

                        st.write(
                            "**Qualification:**",
                            doctor.get("qualification", "N/A")
                        )

                        st.write(
                            "**Experience:**",
                            doctor.get("experience", "N/A")
                        )

                    with col2:
                        st.write(
                            "**Hospital:**",
                            hospital.get("hospital_name", "N/A")
                        )

                        st.write(
                            "**Date:**",
                            appointment_date_value
                        )

                        st.write(
                            "**Time:**",
                            appointment_time_value
                        )

                        st.write("**Status:**")
                        show_status_badge(status)

                    st.write(
                        "**Reason:**",
                        appointment.get("reason", "N/A")
                    )

                    notes = appointment.get("notes")

                    if notes:
                        st.write("**Doctor Notes:**", notes)

                    # -------------------------------------
                    # CANCEL APPOINTMENT
                    # -------------------------------------

                    if status in ["Pending", "Confirmed"]:
                        confirm_cancel = st.checkbox(
                            f"I want to cancel appointment #{appointment_id}",
                            key=f"confirm_cancel_{appointment_id}"
                        )

                        if st.button(
                            "❌ Cancel Appointment",
                            key=f"cancel_appointment_{appointment_id}",
                            use_container_width=True
                        ):
                            if not confirm_cancel:
                                st.warning(
                                    "Please confirm before cancelling."
                                )

                            else:
                                try:
                                    cancel_response = requests.put(
                                        f"{API_URL}/appointments/"
                                        f"{appointment_id}/status",
                                        headers=headers,
                                        json={"status": "Cancelled"},
                                        timeout=10
                                    )

                                    if cancel_response.status_code == 200:
                                        st.success(
                                            "Appointment cancelled successfully!"
                                        )
                                        st.rerun()

                                    elif cancel_response.status_code == 401:
                                        st.error(
                                            "Your session has expired. "
                                            "Please log in again."
                                        )

                                    else:
                                        try:
                                            error_data = cancel_response.json()
                                            st.error(
                                                error_data.get(
                                                    "detail",
                                                    "Unable to cancel appointment."
                                                )
                                            )
                                        except ValueError:
                                            st.error(
                                                "Unable to cancel appointment."
                                            )

                                except requests.exceptions.RequestException as error:
                                    st.error(
                                        f"Request failed: {error}"
                                    )

    elif response.status_code == 401:
        st.error(
            "Your login session has expired. Please log in again."
        )

    elif response.status_code == 404:
        st.warning("Patient profile not found.")

    else:
        try:
            error_data = response.json()
            st.error(
                error_data.get(
                    "detail",
                    "Unable to fetch appointments."
                )
            )
        except ValueError:
            st.error("Unable to fetch appointments.")

except requests.exceptions.RequestException as error:
    st.error(
        "Unable to connect to the backend. Make sure FastAPI is running. "
        f"Details: {error}"
    )
