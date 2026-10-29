
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="Emergency Assistant",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 Emergency Assistant")

st.warning(
    "If you are experiencing a serious or life-threatening emergency, "
    "contact local emergency services or go to the nearest hospital immediately."
)

# Check login
if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.stop()

token = st.session_state.get("access_token")

headers = {
    "Authorization": f"Bearer {token}"
}

st.subheader("Enter Patient Information")

# Patient ID
patient_id = st.number_input(
    "Patient ID",
    min_value=1,
    value=1,
    step=1
)

col1, col2 = st.columns(2)

with col1:
    heart_rate = st.number_input(
        "Heart Rate (BPM)",
        min_value=0,
        max_value=250,
        value=80
    )

    systolic_bp = st.number_input(
        "Systolic Blood Pressure",
        min_value=0,
        max_value=300,
        value=120
    )

    diastolic_bp = st.number_input(
        "Diastolic Blood Pressure",
        min_value=0,
        max_value=200,
        value=80
    )

with col2:
    temperature = st.text_input(
        "Temperature",
        value="98.6"
    )

    oxygen_level = st.number_input(
        "Oxygen Level / SpO2 (%)",
        min_value=0,
        max_value=100,
        value=98
    )

symptoms = st.text_area(
    "Describe Symptoms",
    placeholder="Example: chest pain, difficulty breathing, dizziness..."
)

if st.button("🚨 Assess Emergency Risk", use_container_width=True):

    if not symptoms.strip():
        st.warning("Please describe the symptoms.")
        st.stop()

    # Request payload
    payload = {
        "patient_id": patient_id,
        "heart_rate": heart_rate,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "temperature": temperature,
        "oxygen_level": oxygen_level,
        "symptoms": symptoms
    }

    try:
        response = requests.post(
            f"{API_URL}/emergency/assess",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:

            data = response.json()


            st.success("Emergency assessment completed. ✅")

            st.subheader("📋 Assessment Result")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Risk Score",
                    data.get("risk_score", "N/A")
                )

            with col2:
                st.metric(
                    "Emergency Level",
                    data.get("emergency_level", "N/A")
                )

            st.subheader("🤖 AI Recommendation")

            st.write(
    data.get(
        "recommendation",
        "No recommendation available."
    )
)

            st.error(
                "🚨 Emergency Notice: If you are experiencing severe "
                "symptoms or a medical emergency, contact local emergency "
                "services or visit the nearest hospital immediately. "
                "Do not rely only on this application."
            )

        elif response.status_code == 401:

            st.error(
                "Your login session has expired. Please login again."
            )

        else:

            try:
                error = response.json()

                st.error(
                    error.get(
                        "detail",
                        "Emergency assessment failed."
                    )
                )

            except Exception:
                st.error("Emergency assessment failed.")

    except requests.exceptions.ConnectionError:

        st.error(
            "Backend server is not running. Please start FastAPI first."
        )
