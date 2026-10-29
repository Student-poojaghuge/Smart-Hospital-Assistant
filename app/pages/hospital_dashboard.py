
import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8001"
TIMEOUT = 15

st.set_page_config(
    page_title="Hospital Dashboard",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #f4f7fb;
}
h1, h2, h3 {
    color: #15345b;
}
[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e1e8f0;
}
div.stButton > button {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)


def fetch_data(endpoint):
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        st.error(f"Cannot load {endpoint}: {exc}")
        return None


st.title("🏥 Hospital Management Dashboard")
st.write("Manage hospitals, doctors, and doctor appointments.")

with st.sidebar:
    st.header("Navigation")
    section = st.radio(
        "Choose a section",
        ["Overview", "Hospitals", "Doctors", "Appointments"]
    )
    if st.button("Refresh data"):
        st.rerun()

hospital_response = fetch_data("/hospitals/")
doctor_response = fetch_data("/doctors/")

hospitals = (
    hospital_response.get("hospitals", [])
    if hospital_response else []
)
doctors = (
    doctor_response.get("doctors", [])
    if doctor_response else []
)

if section == "Overview":
    st.subheader("Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Hospitals", len(hospitals))
    col2.metric("Total Doctors", len(doctors))

    specializations = {
        str(d.get("specialization", "")).strip()
        for d in doctors
        if d.get("specialization")
    }
    col3.metric("Specializations", len(specializations))

    st.divider()
    st.subheader("Select a Hospital")

    if hospitals:
        hospital_options = {
            f"{h.get('hospital_name', 'Hospital')} (ID: {h.get('hospital_id')})":
            h for h in hospitals
        }
        selected_name = st.selectbox(
            "Hospital",
            list(hospital_options.keys())
        )
        hospital = hospital_options[selected_name]

        st.markdown(f"### {hospital.get('hospital_name', 'Hospital')}")
        st.write("**Location:**", hospital.get("location") or "Not available")
        st.write("**Address:**", hospital.get("address") or "Not available")
        st.write("**Phone:**", hospital.get("phone") or "Not available")
        st.write("**Type:**", hospital.get("hospital_type") or "Not available")
        st.write(
            "**Emergency Available:**",
            str(hospital.get("emergency_available", "Not available"))
        )

        hospital_id = hospital.get("hospital_id")
        hospital_name = str(hospital.get("hospital_name", "")).strip().lower()

        matching_doctors = [
            d for d in doctors
            if (
                str(d.get("hospital_id", "")) == str(hospital_id)
                or (
                    d.get("hospital_name")
                    and str(d["hospital_name"]).strip().lower() == hospital_name
                )
            )
        ]

        st.subheader("Doctors at this Hospital")
        st.metric("Doctors listed", len(matching_doctors))

        if matching_doctors:
            st.dataframe(pd.DataFrame(matching_doctors), use_container_width=True)
        else:
            st.info("No doctors are currently linked to this hospital.")
    else:
        st.warning("No hospitals were returned by the API.")

elif section == "Hospitals":
    st.subheader("Hospital Directory")

    if hospitals:
        df = pd.DataFrame(hospitals)
        search = st.text_input("Search hospitals by name or location")

        if search:
            mask = df.astype(str).apply(
                lambda col: col.str.contains(search, case=False, na=False)
            ).any(axis=1)
            df = df[mask]

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hospital data is available.")

elif section == "Doctors":
    st.subheader("Doctor Directory")

    if doctors:
        df = pd.DataFrame(doctors)

        specializations = sorted(
            df["specialization"].dropna().astype(str).unique()
        ) if "specialization" in df.columns else []

        selected_specialization = st.selectbox(
            "Filter by specialization",
            ["All"] + specializations
        )

        if selected_specialization != "All" and "specialization" in df.columns:
            df = df[
                df["specialization"].astype(str) == selected_specialization
            ]

        search = st.text_input("Search doctors")
        if search:
            mask = df.astype(str).apply(
                lambda col: col.str.contains(search, case=False, na=False)
            ).any(axis=1)
            df = df[mask]

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No doctor data is available.")

elif section == "Appointments":
    st.subheader("Doctor Appointments")

    if not doctors:
        st.info("No doctors are available to select.")
    else:
        doctor_options = {
            f"Doctor ID {d.get('doctor_id')} — {d.get('specialization', 'General')}":
            d for d in doctors if d.get("doctor_id") is not None
        }

        if not doctor_options:
            st.warning("Doctor IDs were not returned by the API.")
        else:
            selected_doctor_name = st.selectbox(
                "Select Doctor",
                list(doctor_options.keys())
            )
            doctor = doctor_options[selected_doctor_name]
            doctor_id = doctor["doctor_id"]

            summary_response = fetch_data(
                f"/appointments/doctor/{doctor_id}/summary"
            )
            appointments_response = fetch_data(
                f"/appointments/doctor/{doctor_id}"
            )

            if summary_response:
                summary = summary_response.get("summary", summary_response)
                cols = st.columns(4)
                metrics = [
                    ("Total", "total_appointments"),
                    ("Today", "today_appointments"),
                    ("Pending", "pending_appointments"),
                    ("Confirmed", "confirmed_appointments"),
                ]
                for col, (label, key) in zip(cols, metrics):
                    col.metric(label, summary.get(key, 0))

            if appointments_response:
                appointments = appointments_response.get("appointments", [])
                if appointments:
                    df = pd.json_normalize(appointments)
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No appointments found for this doctor.")
