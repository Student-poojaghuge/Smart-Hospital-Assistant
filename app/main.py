
import streamlit as st
import html

from theme import apply_hospital_theme

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Smart Hospital Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_hospital_theme()

# =====================================================
# SESSION STATE
# =====================================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# =====================================================
# CUSTOM UI
# =====================================================

st.markdown("""
<style>
.stApp {
    background: #f2f7fd;
    color: #183657;
}

.block-container {
    max-width: 1500px;
    padding: 1.3rem 1.5rem 2rem;
}

[data-testid="stSidebar"] {
    background: #102b4e;
}

[data-testid="stSidebar"] * {
    color: #ffffff;
}

.hospital-brand {
    text-align: center;
    margin: 0 auto 26px;
}

.hospital-brand h1 {
    color: #15365f;
    font-size: clamp(25px, 3vw, 38px);
    font-weight: 800;
    margin-bottom: 5px;
}

.hospital-brand p {
    color: #496887;
    font-size: 15px;
}

.welcome-card {
    background: white;
    border: 1px solid #d8e6f5;
    border-radius: 15px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 3px 12px #173c6208;
}

.section-title {
    color: #16385f;
    font-size: 22px;
    font-weight: 750;
    margin: 22px 0 14px;
}

.feature-card {
    background: #ffffff;
    border: 1px solid #dce8f5;
    border-radius: 14px;
    padding: 20px;
    min-height: 155px;
    margin-bottom: 12px;
}

.feature-icon {
    font-size: 28px;
    margin-bottom: 10px;
}

.feature-card h3 {
    color: #16385f;
    font-size: 17px;
    margin: 0 0 8px;
}

.feature-card p {
    color: #647990;
    font-size: 13px;
    line-height: 1.6;
    margin: 0;
}

div.stButton > button {
    border-radius: 8px;
    min-height: 42px;
    font-weight: 600;
    border: 1px solid #d5e3f2;
}

div.stButton > button:hover {
    border-color: #1769aa;
    color: #1769aa;
}

.footer-text {
    text-align: center;
    color: #71859a;
    font-size: 12px;
    padding-top: 25px;
}

@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.8rem;
    }

    .welcome-card {
        padding: 18px;
    }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown("""
<div class="hospital-brand">
    <h1>🏥 Smart Hospital Management System</h1>
    <p>AI Powered &nbsp; • &nbsp; Multi-Language
    &nbsp; • &nbsp; Complete Healthcare Solution</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# LOGGED-OUT HOME PAGE
# =====================================================

if not st.session_state["logged_in"]:

    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown("""
        <div class="welcome-card">
            <h2 style="color:#15365f;">
                Better Healthcare for a Healthier Tomorrow
            </h2>
            <p style="color:#526b84; line-height:1.8;">
                Your health matters. Access hospital services,
                medical information, and AI-powered assistance
                through one convenient platform.
            </p>
            <hr>
            <p style="color:#1769aa; line-height:2;">
                ✓ Secure healthcare access<br>
                ✓ AI-powered symptom information<br>
                ✓ Medicine information and appointments<br>
                ✓ English, Marathi, and Hindi support
            </p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="welcome-card" style="text-align:center;">
            <div style="font-size:55px;">👨‍⚕️</div>
            <h2 style="color:#15365f;">Welcome Back!</h2>
            <p style="color:#526b84;">
                Sign in to access your healthcare dashboard.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔐 Open Login Page", use_container_width=True):
            st.switch_page("pages/login.py")

# =====================================================
# LOGGED-IN HOME PAGE
# =====================================================

else:

    user_name = html.escape(
        str(st.session_state.get("name", "User"))
    )
    role = str(st.session_state.get("role", "patient")).lower()

    st.markdown(f"""
    <div class="welcome-card">
        <h2 style="color:#15365f;">Welcome, {user_name}! 👋</h2>
        <p style="color:#526b84;">
            Here is your Smart Hospital Assistant workspace.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Role-aware dashboard links.
    # These links only appear when the matching page exists.
    st.markdown(
        '<div class="section-title">Your Healthcare Workspace</div>',
        unsafe_allow_html=True
    )

    if role == "admin":
        pages = [
            ("🛡️", "Admin Dashboard", "pages/admin_dashboard.py"),
            ("👨‍⚕️", "Doctor Dashboard", "pages/doctor_dashboard.py"),
            ("👤", "Patient Dashboard", "pages/patient_dashboard.py"),
        ]
    elif role == "doctor":
        pages = [
            ("🩺", "Doctor Dashboard", "pages/doctor_dashboard.py"),
            ("📅", "Appointments", "pages/appointments.py"),
            ("📋", "Medical Records", "pages/medical_records.py"),
        ]
    else:
        pages = [
            ("👤", "Patient Dashboard", "pages/patient_dashboard.py"),
            ("📅", "Appointments", "pages/appointments.py"),
            ("📋", "Medical Records", "pages/medical_records.py"),
        ]

    columns = st.columns(3, gap="medium")

    for i, (icon, label, page) in enumerate(pages):
        with columns[i]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <h3>{label}</h3>
                <p>Open your hospital workspace and available services.</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(
                f"Open {label}",
                key=f"open_page_{i}",
                use_container_width=True
            ):
                try:
                    st.switch_page(page)
                except Exception:
                    st.error(
                        f"Could not open {page}. "
                        "Check that the page exists in app/pages."
                    )

    st.markdown(
        '<div class="section-title">AI & Healthcare Tools</div>',
        unsafe_allow_html=True
    )

    tool_columns = st.columns(3, gap="medium")

    tools = [
        ("🤖", "Medical AI Assistant",
         "Get AI-supported health information.",
         "pages/medical_assistant.py"),
        ("💬", "Chat History",
         "Review your previous assistant conversations.",
         "pages/chat_history.py"),
        ("🚨", "Emergency Assessment",
         "Access the emergency assessment module.",
         "pages/emergency.py"),
    ]

    for i, (icon, title, description, page) in enumerate(tools):
        with tool_columns[i]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(
                f"Open {title}",
                key=f"open_tool_{i}",
                use_container_width=True
            ):
                try:
                    st.switch_page(page)
                except Exception:
                    st.error(
                        f"Could not open {page}. "
                        "Verify the existing page path."
                    )

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")

# =====================================================
# FOOTER
# =====================================================

st.markdown("""
<div class="footer-text">
    Smart Hospital Management System
    <br>
    Educational project. Consult a qualified healthcare
    professional for medical decisions.
</div>
""", unsafe_allow_html=True)
