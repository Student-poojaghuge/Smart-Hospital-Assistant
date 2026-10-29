
import streamlit as st


def apply_hospital_theme():
    st.markdown(
        """
        <style>
        /* Global hospital background */
        .stApp {
            background: linear-gradient(
                135deg,
                #EAF3FF 0%,
                #F5F8FD 50%,
                #E6F4F7 100%
            );
            color: #17345C;
        }

        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
            max-width: 1440px;
        }

        h1, h2, h3, h4 {
            color: #17345C !important;
            font-weight: 700 !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: #142E50;
        }

        [data-testid="stSidebar"] * {
            color: #F7FAFF;
        }

        /* Dashboard metric cards */
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #D9E7F5;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 5px 18px rgba(20, 46, 80, 0.07);
        }

        [data-testid="stMetricLabel"] {
            color: #617894 !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
        }

        [data-testid="stMetricValue"] {
            color: #17345C !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }

        [data-testid="stMetricDelta"] {
            font-weight: 600;
        }

        /* Streamlit bordered containers */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #FFFFFF;
            border: 1px solid #D9E7F5;
            border-radius: 16px;
            padding: 14px;
            box-shadow: 0 5px 18px rgba(20, 46, 80, 0.05);
        }

        /* Buttons */
        .stButton > button,
        .stFormSubmitButton > button {
            background: #2476E8;
            color: #FFFFFF !important;
            border: 1px solid #2476E8;
            border-radius: 9px;
            min-height: 40px;
            font-weight: 600;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            background: #185EC4;
            border-color: #185EC4;
            color: #FFFFFF !important;
        }

        /* Form inputs */
        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stTimeInput input,
        .stTextArea textarea {
            background: #FFFFFF;
            border: 1px solid #D5E1F0;
            border-radius: 8px;
            color: #17345C;
        }

        [data-baseweb="select"] > div {
            border-radius: 8px;
            border-color: #D5E1F0;
        }

        /* Tables and alerts */
        [data-testid="stDataFrame"],
        [data-testid="stTable"] {
            border: 1px solid #DFE9F5;
            border-radius: 10px;
            overflow: hidden;
        }

        [data-testid="stAlert"] {
            border-radius: 10px;
        }

        hr {
            border-color: #DFE9F5;
        }

        /* Login heading */
        .login-title {
            color: #17345C !important;
            font-size: 1.8rem;
            font-weight: 700;
            text-align: center;
        }

        .login-subtitle {
            color: #627895 !important;
            text-align: center;
            font-size: 0.95rem;
        }

        /* Responsive layout */
        @media (max-width: 768px) {
            .block-container {
                padding: 1rem 0.8rem 2rem;
            }

            h1 {
                font-size: 1.7rem !important;
            }

            h2 {
                font-size: 1.4rem !important;
            }

            [data-testid="stMetric"] {
                padding: 12px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
