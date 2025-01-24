# functions/style.py
import streamlit as st

def set_custom_style():
    """Carrega o estilo CSS customizado."""
    st.markdown(
        """
        <style>
        .main {
            background-color: #f0f2f6;
            padding-top: 2rem;
        }
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .big-title {
            color: #2c3e50;
            font-size: 40px;
            font-weight: bold;
            margin-bottom: 30px;
            text-align: center;
            padding: 20px;
            background-color: #ecf0f1;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stSubheader {
            color: #34495e;
            font-size: 28px;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 15px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .stButton>button {
            background-color: #3498db;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 12px 24px;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #2980b9;
        }
        .stTextInput>div>div>input, .stSelectbox>div>div>select {
            border-radius: 8px;
            border: 2px solid #bdc3c7;
            padding: 10px;
        }
        .custo {
            color: #27ae60;
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            margin-top: 20px;
            padding: 10px;
            background-color: #e8f6e9;
            border-radius: 10px;
        }
        /* Ocultar o título do selectbox */
        div[data-baseweb="select"] > label {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
