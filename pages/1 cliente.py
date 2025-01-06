import streamlit as st
from functions.layout import show_logo, set_page_config
from functions.helpers import valida_campos
from functions.style import set_custom_style

st.set_page_config(page_title="1: Identificação do Cliente", layout="wide")
set_custom_style()
show_logo()

def passo_cliente():
    st.markdown('<h3 class="stSubheader">Identificação do Cliente</h3>', unsafe_allow_html=True)
    
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
        if valida_campos(nome_cliente, nome_empresa):
            st.session_state["respostas"]["Solicitante"] = nome_cliente.strip()
            st.session_state["respostas"]["Empresa"] = nome_empresa.strip()
            st.success("Dados salvos com sucesso!")
        else:
            st.error("Por favor, preencha ambos os campos.")

if __name__ == "__main__":
    passo_cliente()
