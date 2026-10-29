
import streamlit as st

st.set_page_config(
    page_title="Language Selection",
    page_icon="🌐",
    layout="centered"
)

st.title("🌐 Select Language")
st.write("Choose your preferred language")

st.divider()

# =========================
# Language Selection
# =========================

language = st.radio(
    "Select Language",
    [
        "🇬🇧 English",
        "🇮🇳 मराठी",
        "🇮🇳 हिंदी"
    ]
)

st.divider()

# =========================
# Continue Button
# =========================

if st.button(
    "Continue ➜",
    use_container_width=True
):

    if language == "🇬🇧 English":
        selected_language = "English"

    elif language == "🇮🇳 मराठी":
        selected_language = "Marathi"

    else:
        selected_language = "Hindi"

    # Save selected language
    st.session_state["language"] = selected_language

    st.success(
        f"Language selected: {selected_language}"
    )

    st.info(
        "Your language preference has been saved."
    )
