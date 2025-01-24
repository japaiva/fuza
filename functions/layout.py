# functions/layout.py
import streamlit as st

def show_logo():
    """Exibe o logo na barra lateral."""
    st.sidebar.image("assets/logo.png", width=150)
