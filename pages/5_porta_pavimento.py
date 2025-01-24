import streamlit as st
from functions.layout import show_logo
from functions.style import set_custom_style
from functions.auth import check_auth
from functions.page_utils import get_current_page_name

st.set_page_config(page_title="5: Porta do Pavimento", layout="wide")
set_custom_style()
show_logo()

current_page = get_current_page_name()
if current_page:
    st.session_state['current_page'] = current_page

check_auth()

def porta_pav():
    st.markdown('<h3 class="stSubheader">Detalhes Porta Pavimento</h3>', unsafe_allow_html=True)

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

        if modelo in ["Automática", "Pivotante"]:
            material_options = ["Inox", "Chapa Pintada", "Alumínio"]
            default_material = st.session_state["respostas"].get("Material Porta Pavimento", "Inox")
            if default_material not in material_options:
                default_material = "Inox"
            material = st.selectbox(
                "Material:",
                options=material_options,
                index=material_options.index(default_material),
                key="material_porta_pav"
            )
        elif modelo == "Rampa":
            material_options = ["Com aço", "Sem aço"]
            default_material = st.session_state["respostas"].get("Material Porta Pavimento", "Com aço")
            if default_material not in material_options:
                default_material = "Com aço"
            material = st.selectbox(
                "Material:",
                options=material_options,
                index=material_options.index(default_material),
                key="material_porta_pav"
            )

        if modelo == "Automática":
            folhas = st.selectbox(
            "Folhas:",
            options=["2", "3", "4","Central"],
            index=["2", "3", "4","Central"].index(st.session_state["respostas"].get("Folhas Porta Pavimento", "2")),
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
        if modelo in ["Automática", "Pivotante", "Rampa"]:
            st.session_state["respostas"]["Material Porta Pavimento"] = material
        else:
            st.session_state["respostas"].pop("Material Porta Pavimento", None)
        if modelo == "Automática":
            st.session_state["respostas"]["Folhas Porta Pavimento"] = folhas
        else:
            st.session_state["respostas"].pop("Folhas Porta Pavimento", None)
        st.session_state["respostas"]["Altura Porta Pavimento"] = altura
        st.session_state["respostas"]["Largura Porta Pavimento"] = largura
        
        st.switch_page("Simulador.py")
        st.rerun()

if __name__ == "__main__":
    porta_pav()