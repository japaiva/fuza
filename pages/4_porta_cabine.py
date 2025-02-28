import streamlit as st
from functions.layout import show_logo
from functions.style import set_custom_style
from functions.auth import check_auth
from functions.page_utils import get_current_page_name

st.set_page_config(page_title="4: Porta da Cabine", layout="wide")
set_custom_style()
show_logo()

current_page = get_current_page_name()
if current_page:
    st.session_state['current_page'] = current_page

check_auth()

def porta_cabine():
    st.markdown('<h3 class="stSubheader">Detalhes Porta Cabine</h3>', unsafe_allow_html=True)

    if "respostas" not in st.session_state:
        st.session_state["respostas"] = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        modelo = st.selectbox(
            "Modelo:",
            options=["Automática", "Pantográfica", "Pivotante", "Guilhotina", "Camarão", "Cancela", "Rampa"],
            index=["Automática", "Pantográfica", "Pivotante", "Guilhotina", "Camarão", "Cancela", "Rampa"].index(st.session_state["respostas"].get("Modelo Porta", "Automática")),
            key="modelo_porta"
        )

        if modelo in ["Automática", "Pivotante"]:
            material = st.selectbox(
                "Material:",
                options=["Inox", "Chapa Pintada", "Alumínio"],
                index=["Inox", "Chapa Pintada", "Alumínio"].index(st.session_state["respostas"].get("Material Porta", "Inox")),
                key="material_porta"
            )
        elif modelo == "Rampa":
            material = st.selectbox(
                "Material:",
                options=["Com aço", "Sem aço"],
                index=["Com aço", "Sem aço"].index(st.session_state["respostas"].get("Material Porta", "Com aço")),
                key="material_porta"
            )

        if modelo == "Automática":
            folhas = st.selectbox(
                "Folhas:",
                options=["2", "3","4", "Central"],
                index=["2", "3","4", "Central"].index(st.session_state["respostas"].get("Folhas Porta", "2")),
                key="folhas_porta"
            )

    with col2:
        altura = st.number_input(
            "Altura (m):",
            min_value=0.1,
            max_value=5.0,
            value=float(st.session_state["respostas"].get("Altura Porta", 2.0)),
            step=0.01,
            format="%.2f",
            key="altura_porta"
        )

        largura = st.number_input(
            "Largura (m):",
            min_value=0.1,
            max_value=5.0,
            value=float(st.session_state["respostas"].get("Largura Porta", 0.8)),
            step=0.01,
            format="%.2f",
            key="largura_porta"
        )

    if st.button("Salvar", key="salvar_porta_cabine"):
        st.session_state["respostas"]["Modelo Porta"] = modelo
        if modelo in ["Automática", "Pivotante", "Rampa"]:
            st.session_state["respostas"]["Material Porta"] = material
        else:
            st.session_state["respostas"].pop("Material Porta", None)
        if modelo == "Automática":
            st.session_state["respostas"]["Folhas Porta"] = folhas
        else:
            st.session_state["respostas"].pop("Folhas Porta", None)
        st.session_state["respostas"]["Altura Porta"] = altura
        st.session_state["respostas"]["Largura Porta"] = largura

        st.switch_page("pages/5_porta_pavimento.py")
        st.rerun()

if __name__ == "__main__":
    porta_cabine()