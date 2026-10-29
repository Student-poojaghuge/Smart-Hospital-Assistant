
import streamlit as st


def apply_accessibility():
    large_text = st.session_state.get(
        "large_text_mode", False
    )

    high_contrast = st.session_state.get(
        "high_contrast_mode", False
    )

    css = ""

    if large_text:
        css += """
        .stApp p,
        .stApp label,
        .stApp button,
        .stApp input,
        .stApp textarea {
            font-size: 20px !important;
        }

        .stApp h1 { font-size: 42px !important; }
        .stApp h2 { font-size: 34px !important; }
        .stApp h3 { font-size: 28px !important; }
        """

    if high_contrast:
        css += """
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"],
        [data-testid="stSidebar"] {
            background-color: #000000 !important;
            color: #FFFFFF !important;
        }

        .stApp p,
        .stApp label,
        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp span,
        .stApp li {
            color: #FFFFFF !important;
        }

        .stApp button {
            background-color: #FFFF00 !important;
            color: #000000 !important;
            border: 2px solid #FFFFFF !important;
        }
        """

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )
