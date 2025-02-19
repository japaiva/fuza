import streamlit as st
from functions.layout import show_logo
from functions.style import set_custom_style
from functions.auth import check_auth
from functions.page_utils import get_current_page_name

st.set_page_config(page_title="3: Cabine", layout="wide")
set_custom_style()
show_logo()

current_page = get_current_page_name()
if current_page:
    st.session_state['current_page'] = current_page

check_auth()

def cabine_corpo():
    st.markdown('<h3 class="stSubheader">Detalhes Cabine</h3>', unsafe_allow_html=True)

    if "respostas" not in st.session_state:
        st.session_state["respostas"] = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        material = st.selectbox(
            "Material:",
            options=["Inox", "Chapa Pintada", "Alumínio"],
            index=["Inox", "Chapa Pintada", "Alumínio"].index(st.session_state["respostas"].get("Material", "Inox")),
            key="material"
        )

        if material == "Inox":
            tipo_inox = st.selectbox(
                "Tipo de Inox:",
                options=["304", "430"],
                index=["304", "430"].index(st.session_state["respostas"].get("Tipo de Inox", "430")),
                key="tipo_inox"
            )

        espessura = st.number_input(
            "Espessura (mm):",
            min_value=0.1,
            max_value=5.0,
            value=float(st.session_state["respostas"].get("Espessura", 1.2)),
            step=0.1,
            format="%.1f",
            key="espessura"
        )


    with col2:
        modelo_elevador = st.session_state["respostas"].get("Modelo do Elevador", "")
        altura_inicial = 2.30 if modelo_elevador == "Passageiro" else 2.10
        altura_cabine = st.number_input(
            "Altura da Cabine (m):",
            min_value=0.01,
            max_value=5.0,
            value=float(st.session_state["respostas"].get("Altura da Cabine", altura_inicial)),
            step=0.01,
            format="%.2f",
            key="altura_cabine"
        )

        saida = st.selectbox(
            "Saída:",
            options=["Padrão", "Oposta"],
            index=["Padrão", "Oposta"].index(st.session_state["respostas"].get("Saída", "Padrão")),
            key="saida"
        )


        piso = st.selectbox(
            "Piso:",
            options=["Por conta do cliente", "Por conta da empresa"],
            index=["Por conta do cliente", "Por conta da empresa"].index(st.session_state["respostas"].get("Piso", "Por conta do cliente")),
            key="piso"
        )

        if piso == "Por conta da empresa":
            material_piso = st.selectbox(
                "Material do Piso da Cabine:",
                options=["Xadrez", "Antiderrapante 3/8"],
                index=["Xadrez", "Antiderrapante 3/8"].index(st.session_state["respostas"].get("Material Piso Cabine", "Xadrez")),
                key="material_piso"
            )

    if st.button("Salvar", key="salvar_cabine_corpo"):
        if altura_cabine > 0:
            st.session_state["respostas"]["Material"] = material
            if material == "Inox":
                st.session_state["respostas"]["Tipo de Inox"] = tipo_inox
            else:
                st.session_state["respostas"].pop("Tipo de Inox", None)
            st.session_state["respostas"]["Espessura"] = espessura
            st.session_state["respostas"]["Saída"] = saida
            st.session_state["respostas"]["Altura da Cabine"] = altura_cabine
            st.session_state["respostas"]["Piso"] = piso
            if piso == "Por conta da empresa":
                st.session_state["respostas"]["Material Piso Cabine"] = material_piso
            else:
                st.session_state["respostas"].pop("Material Piso Cabine", None)

            st.switch_page("pages/4_porta_cabine.py")
            st.rerun()
        else:
            st.error("A altura da cabine deve ser maior que zero.")

if __name__ == "__main__":
    cabine_corpo()