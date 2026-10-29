import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="Medical Assistant",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Smart Hospital Assistant")
st.subheader("🤖 Medical Knowledge Assistant")

# Check login
if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.stop()

# Get token automatically
token = st.session_state.get("access_token")

headers = {
    "Authorization": f"Bearer {token}"
}

query = st.text_area(
    "Ask your medical question:",
    placeholder="Example: What are the common symptoms of diabetes?"
)

top_k = st.slider(
    "Number of knowledge results",
    min_value=1,
    max_value=5,
    value=3
)

if st.button("Ask Assistant", use_container_width=True):

    if not query.strip():
        st.warning("Please enter a question.")
        st.stop()

    try:
        response = requests.post(
            f"{API_URL}/rag/assistant",
            headers=headers,
            json={
                "query": query,
                "top_k": top_k
            }
        )

        if response.status_code == 200:
            data = response.json()

            st.success("Assistant response generated successfully.")

            st.write("### 🤖 Assistant Type")
            st.write(data["assistant_type"])

            st.write("### 💬 Response")
            st.write(data["chat"]["response"])

            if data.get("emergency"):
                st.error(
                    "🚨 Emergency: If this is a real medical emergency, "
                    "contact local emergency services or visit the nearest hospital immediately."
                )



        elif response.status_code == 401:
            st.error(
                "Your login session has expired. Please login again."
            )

        else:
            try:
                error = response.json()
                st.error(error.get("detail", "Something went wrong."))
            except Exception:
                st.error("Something went wrong.")

    except requests.exceptions.ConnectionError:
        st.error(
            "Backend server is not running. Please start FastAPI first."
        )
