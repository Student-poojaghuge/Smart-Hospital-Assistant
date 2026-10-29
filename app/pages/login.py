
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="Login - Smart Hospital Assistant",
    page_icon="🏥",
    layout="centered"
)

# Apply the shared hospital theme
from theme import apply_hospital_theme
apply_hospital_theme()


# Center the login card
st.write("")
left, center, right = st.columns([1, 3, 1])

with center:
    with st.container(border=True):

        st.markdown(
            '<div class="login-title">🏥 Smart Hospital Assistant</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="login-subtitle">'
            'Your healthcare companion</div>',
            unsafe_allow_html=True
        )

        st.write("")
        st.subheader("Welcome Back")
        st.caption("Sign in to continue to your account.")

        if st.session_state.get("logged_in", False):

            st.success(
                f"You are already logged in as "
                f"{st.session_state.get('name', 'User')}."
            )

            if st.button(
                "Go to Medical Assistant",
                use_container_width=True
            ):
                st.switch_page("pages/medical_assistant.py")

            st.stop()

        email = st.text_input(
            "Email",
            placeholder="Enter your email"
        ).strip()

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        st.write("")

        if st.button("Login", use_container_width=True):

            if not email or not password:
                st.warning("Please enter email and password.")

            else:
                try:
                    response = requests.post(
                        f"{API_URL}/auth/login",
                        json={
                            "email": email,
                            "password": password
                        }
                    )

                    if response.status_code == 200:
                        data = response.json()

                        st.session_state["access_token"] = data["access_token"]
                        st.session_state["user_id"] = data["user_id"]
                        st.session_state["name"] = data["name"]
                        st.session_state["email"] = data["email"]
                        st.session_state["role"] = data["role"]
                        st.session_state["logged_in"] = True

                        st.success("Login successful! ✅")

                        st.switch_page(
                            "pages/medical_assistant.py"
                        )

                    else:
                        st.error(
                            f"Status Code: {response.status_code}"
                        )
                        st.write("Response:", response.text)

                        try:
                            error = response.json()
                            st.error(
                                error.get("detail", "Login failed.")
                            )
                        except Exception:
                            st.error("Login failed.")

                except requests.exceptions.ConnectionError:
                    st.error(
                        "Backend server is not running. "
                        "Please start FastAPI first."
                    )
