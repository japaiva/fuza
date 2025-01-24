# functions/auth.py
import streamlit as st
from .database import verify_password, get_user

def verify_login(username, password, config):
    user = get_user(username)
    if user and verify_password(password, user.password):
        st.session_state['authentication_status'] = True
        st.session_state['username'] = username
        st.session_state['nivel'] = getattr(user, 'nivel', 'vendedor')  # Define como 'vendedor' se 'nivel' não existir
        return True
    return False

def check_auth():
    """
    Se o usuário não estiver autenticado, redireciona para a página Simulador.
    Essa checagem pode ser chamada no topo das páginas internas.
    """
    if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
        if 'current_page' in st.session_state:
            st.session_state['return_to'] = st.session_state['current_page']
        st.switch_page("Simulador.py")

def is_admin_user(username: str) -> bool:
    """Consulta no BD se o usuário é admin."""
    user = get_user(username)
    return bool(user and user.is_admin)

def logout():
    """Efetua logout limpando o estado da sessão."""
    st.session_state['authentication_status'] = None
    st.session_state['username'] = None
