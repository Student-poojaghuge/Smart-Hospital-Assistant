import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="Chat History - Smart Hospital Assistant",
    page_icon="💬",
    layout="wide"
)

st.title("💬 Chat History")

# Check login
if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.stop()

# Get logged-in user's token
token = st.session_state.get("access_token")

headers = {
    "Authorization": f"Bearer {token}"
}

try:
    response = requests.get(
        f"{API_URL}/chat-history/my-history",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()

        st.success(
            f"Total conversations: {data['total_chats']}"
        )

        history = data.get("history", [])

        if not history:
            st.info("No chat history found.")

        else:
            for chat in history:
                with st.expander(
                    f"Chat #{chat['chat_id']} — {chat['created_at']}"
                ):
                    st.write("### 👤 Your Question")
                    st.write(chat["query"])

                    st.write("### 🤖 Assistant Response")
                    st.markdown(chat["response"])

                    st.write("### 📌 Query Type")
                    st.write(chat["query_type"])

                    st.divider()

    elif response.status_code == 401:
        st.error("Your login session has expired. Please login again.")

    else:
        try:
            error = response.json()
            st.error(error.get("detail", "Unable to fetch chat history."))
        except Exception:
            st.error("Unable to fetch chat history.")

except requests.exceptions.ConnectionError:
    st.error(
        "Backend server is not running. Please start FastAPI first."
    )