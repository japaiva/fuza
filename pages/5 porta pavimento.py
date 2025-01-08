import streamlit as st
from functions.layout import show_logo, set_page_config
from functions.style import set_custom_style

st.set_page_config(page_title="5: Porta do Pavimento", layout="wide")
set_custom_style()
show_logo()

def porta_pav():
    st.markdown('<h3 class="stSubheader">Detalhes da Porta do Pavimento</h3>', unsafe_allow_html=True)

    if "respostas" not in st.session_state:
        st.session_state["respostas"] = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        modelo = st.selectbox(
            "Modelo:",
            options=["Automática", "Pantográfica", "Pivotante", "Guilhotina", "Camarão", "Cancela", "Rampa"],
            index=["Automática", "Pantográfica", "Pivotante", "Guilhotina", "Camarão", "Cancela", "Rampa"].index(st.session_state["respostas"].get("Modelo Porta Pavimento", "Automática")),
            key="modelo_porta_pav"
        )

        material = st.selectbox(
            "Material:",
            options=["Inox", "Chapa Pintada", "Alumínio"],
            index=["Inox", "Chapa Pintada", "Alumínio"].index(st.session_state["respostas"].get("Material Porta Pavimento", "Inox")),
            key="material_porta_pav"
        )

        folhas = st.selectbox(
            "Folhas:",
            options=["2", "3", "Central"],
            index=["2", "3", "Central"].index(st.session_state["respostas"].get("Folhas Porta Pavimento", "2")),
            key="folhas_porta_pav"
        )

    with col2:
        altura = st.number_input(
            "Altura (m):",
            min_value=0.1,
            max_value=5.0,
            value=float(st.session_state["respostas"].get("Altura Porta Pavimento", 2.0)),
            step=0.01,
            format="%.2f",
            key="altura_porta_pav"
        )

        largura = st.number_input(
            "Largura (m):",
            min_value=0.1,
            max_value=5.0,
            value=float(st.session_state["respostas"].get("Largura Porta Pavimento", 0.8)),
            step=0.01,
            format="%.2f",
            key="largura_porta_pav"
        )

    if st.button("Salvar", key="salvar_porta_pav"):
        st.session_state["respostas"]["Modelo Porta Pavimento"] = modelo
        st.session_state["respostas"]["Material Porta Pavimento"] = material
        if material == "Inox":
            st.session_state["respostas"]["Tipo de Inox Porta Pavimento"] = tipo_inox
        st.session_state["respostas"]["Folhas Porta Pavimento"] = folhas
        st.session_state["respostas"]["Altura Porta Pavimento"] = altura
        st.session_state["respostas"]["Largura Porta Pavimento"] = largura
        st.success("Detalhes da porta do pavimento salvos com sucesso!")

if __name__ == "__main__":
    porta_pav()