# pages/1_cliente.py
import streamlit as st
from functions.layout import show_logo
from functions.style import set_custom_style
from functions.auth import check_auth
from functions.helpers import valida_campos
from functions.page_utils import get_current_page_name

st.set_page_config(page_title="1: Cliente", layout="wide")
set_custom_style()
show_logo()

current_page = get_current_page_name()
if current_page:
    st.session_state['current_page'] = current_page

check_auth()

def passo_cliente():
    st.markdown('<h3 class="stSubheader">Identificação Cliente</h3>', unsafe_allow_html=True)
    
    if "respostas" not in st.session_state:
        st.session_state["respostas"] = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        nome_cliente = st.text_input(
            "Nome do Solicitante:",
            value=st.session_state["respostas"].get("Solicitante", "")
        )
    
    with col2:
        nome_empresa = st.text_input(
            "Nome da Empresa:",
            value=st.session_state["respostas"].get("Empresa", "")
        )
  
    if st.button("Salvar", key="salvar_cliente"):
        if valida_campos(nome_cliente):
            st.session_state["respostas"]["Solicitante"] = nome_cliente.strip()
            if nome_empresa:
                st.session_state["respostas"]["Empresa"] = nome_empresa.strip()

            st.switch_page("pages/2_elevador.py")
            st.rerun()
        else:
            st.error("Por favor, identifique o cliente.")

if __name__ == "__main__":
    passo_cliente()

