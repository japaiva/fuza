# layout.py
import streamlit as st

def show_logo():
    st.sidebar.image("assets/logo.png", width=150)

def set_page_config():
    st.set_page_config(
        page_title="SCP - Fuza Elevadores",
        layout="wide"
    )