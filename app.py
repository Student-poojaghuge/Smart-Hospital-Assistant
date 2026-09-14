import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Smart Hospital Assistant",
    page_icon="🏥",
    layout="wide"
)

# Header
st.title("🏥 Smart Hospital Assistant")

st.subheader(
    "AI-Powered Healthcare & Emergency Decision Support System"
)

st.markdown("---")

# Welcome section
st.header("Welcome 👋")

st.write(
    """
    Smart Hospital Assistant is an AI-based healthcare support system
    designed to provide preliminary health risk assessment, emergency
    risk detection, doctor consultation support, medicine information,
    appointment management and AI-powered medical assistance.
    """
)

# Features
st.header("🚀 Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(
        """
        ### 🩺 Health Assessment

        Enter symptoms and basic health information
        for preliminary risk assessment.
        """
    )

with col2:
    st.warning(
        """
        ### 🚨 Emergency Detection

        Identify potentially high-risk situations
        and guide the user toward professional help.
        """
    )

with col3:
    st.success(
        """
        ### 👨‍⚕️ Doctor Support

        Manage appointments, patient information
        and AI-assisted clinical information.
        """
    )

# More features
st.markdown("---")

st.header("💡 Future Modules")

features = [
    "🤖 Disease Risk Prediction",
    "🚨 Emergency Risk Assessment",
    "🏠 Home Health Assessment",
    "💊 Medicine Information",
    "📅 Smart Appointment System",
    "🧠 AI Medical Assistant",
    "📊 Hospital Analytics",
    "🔍 Explainable AI"
]

for feature in features:
    st.write(f"• {feature}")

# Disclaimer
st.markdown("---")

st.warning(
    """
    ⚠️ Medical Disclaimer

    This application is an academic and decision-support prototype.
    It does not replace professional medical diagnosis, treatment,
    or emergency medical services.
    """
)