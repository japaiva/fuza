import streamlit as st
from functions.layout import show_logo
from functions.style import set_custom_style
from functions.auth import check_auth
from functions.page_utils import get_current_page_name

st.set_page_config(page_title="Portas do Elevador", layout="wide")
set_custom_style()
show_logo()

current_page = get_current_page_name()
if current_page:
    st.session_state['current_page'] = current_page

check_auth()

def portas():
    st.markdown('<h3 class="stSubheader">Detalhes Portas</h3>', unsafe_allow_html=True)

    if "respostas" not in st.session_state:
        st.session_state["respostas"] = {}

    # Criação das 3 colunas
    col1, col2, col3 = st.columns(3)

    # COLUNA 1: Configuração da Porta da Cabine
    with col1:

        modelo_porta = st.selectbox(
            "Modelo Porta Cabine:",
            options=["Automática", "Pantográfica", "Pivotante", "Guilhotina", "Camarão", "Cancela", "Rampa"],
            index=["Automática", "Pantográfica", "Pivotante", "Guilhotina", "Camarão", "Cancela", "Rampa"].index(
                st.session_state["respostas"].get("Modelo Porta", "Automática")
            ),
            key="modelo_porta"
        )

        material_options = ["Inox", "Chapa Pintada", "Alumínio", "Outro"]
        material_porta = st.selectbox(
            "Material:",
            options=material_options,
            index=material_options.index(st.session_state["respostas"].get("Material Porta", "Inox")),
            key="material_porta"
        )

        if material_porta == "Outro":
            outro_nome_porta = st.text_input(
                "Nome do Material:",
                value=st.session_state["respostas"].get("Material Porta Outro Nome", ""),
                key="material_porta_outro_nome"
            )
            outro_valor_porta = st.number_input(
                "Valor do Material:",
                min_value=0.0,
                value=float(st.session_state["respostas"].get("Material Porta Outro Valor", 0.0)),
                step=0.1,
                format="%.2f",
                key="material_porta_outro_valor"
            )

        folhas_porta = st.selectbox(
            "Folhas da Porta:",
            options=["2", "3", "Central"],
            index=["2", "3", "Central"].index(
                st.session_state["respostas"].get("Folhas Porta", "2")
            ),
            key="folhas_porta"
        ) if modelo_porta == "Automática" else None

    # COLUNA 2: Configuração da Porta do Pavimento
    with col2:

        modelo_porta_pav = st.selectbox(
            "Modelo Porta Pavimento:",
            options=["Automática", "Pantográfica", "Pivotante", "Guilhotina", "Camarão", "Cancela", "Rampa"],
            index=["Automática", "Pantográfica", "Pivotante", "Guilhotina", "Camarão", "Cancela", "Rampa"].index(
                st.session_state["respostas"].get("Modelo Porta Pavimento", "Automática")
            ),
            key="modelo_porta_pav"
        )

        material_options_pav = ["Inox", "Chapa Pintada", "Alumínio", "Outro"]
        material_porta_pav = st.selectbox(
            "Material:",
            options=material_options_pav,
            index=material_options_pav.index(st.session_state["respostas"].get("Material Porta Pavimento", "Inox")),
            key="material_porta_pav"
        )

        if material_porta_pav == "Outro":
            outro_nome_porta_pav = st.text_input(
                "Nome do Material:",
                value=st.session_state["respostas"].get("Material Porta Pavimento Outro Nome", ""),
                key="material_porta_pav_outro_nome"
            )
            outro_valor_porta_pav = st.number_input(
                "Valor do Material:",
                min_value=0.0,
                value=float(st.session_state["respostas"].get("Material Porta Pavimento Outro Valor", 0.0)),
                step=0.1,
                format="%.2f",
                key="material_porta_pav_outro_valor"
            )

        folhas_porta_pav = st.selectbox(
            "Folhas da Porta:",
            options=["2", "3", "Central"],
            index=["2", "3", "Central"].index(
                st.session_state["respostas"].get("Folhas Porta Pavimento", "2")
            ),
            key="folhas_porta_pav"
        ) if modelo_porta_pav == "Automática" else None

    # COLUNA 3: Dimensões das Portas (Cabine e Pavimento)
    with col3:

        largura_porta = st.number_input(
            "Largura Porta Cabine (m):",
            min_value=0.1,
            max_value=5.0,
            value=float(st.session_state["respostas"].get("Largura Porta", 0.8)),
            step=0.01,
            format="%.2f",
            key="largura_porta"
        )

        altura_porta = st.number_input(
            "Altura Porta Cabine (m):",
            min_value=0.1,
            max_value=5.0,
            value=float(st.session_state["respostas"].get("Altura Porta", 2.0)),
            step=0.01,
            format="%.2f",
            key="altura_porta"
        )

        largura_porta_pav = st.number_input(
            "Largura Porta Pavimento (m):",
            min_value=0.1,
            max_value=5.0,
            value=float(st.session_state["respostas"].get("Largura Porta Pavimento", 0.8)),
            step=0.01,
            format="%.2f",
            key="largura_porta_pav"
        )

        altura_porta_pav = st.number_input(
            "Altura Porta Pavimento (m):",
            min_value=0.1,
            max_value=5.0,
            value=float(st.session_state["respostas"].get("Altura Porta Pavimento", 2.0)),
            step=0.01,
            format="%.2f",
            key="altura_porta_pav"
        )

    # Botão para salvar as informações e avançar
    if st.button("Salvar", key="salvar_configuracao_portas"):
        st.session_state["respostas"]["Modelo Porta"] = modelo_porta
        st.session_state["respostas"]["Modelo Porta Pavimento"] = modelo_porta_pav

        # Porta da cabine
        st.session_state["respostas"]["Material Porta"] = material_porta
        if material_porta == "Outro":
            st.session_state["respostas"]["Material Porta Outro Nome"] = outro_nome_porta
            st.session_state["respostas"]["Material Porta Outro Valor"] = outro_valor_porta

        if modelo_porta in ["Automática", "Pivotante", "Rampa"]:
            st.session_state["respostas"]["Material Porta"] = material_porta
        else:
            st.session_state["respostas"].pop("Material Porta", None)

        if modelo_porta == "Automática":
            st.session_state["respostas"]["Folhas Porta"] = folhas_porta
        else:
            st.session_state["respostas"].pop("Folhas Porta", None)

        st.session_state["respostas"]["Altura Porta"] = altura_porta
        st.session_state["respostas"]["Largura Porta"] = largura_porta

        # Porta do pavimento
        st.session_state["respostas"]["Material Porta Pavimento"] = material_porta_pav
        if material_porta_pav == "Outro":
            st.session_state["respostas"]["Material Porta Pavimento Outro Nome"] = outro_nome_porta_pav
            st.session_state["respostas"]["Material Porta Pavimento Outro Valor"] = outro_valor_porta_pav
        else:
            st.session_state["respostas"].pop("Material Porta Pavimento Outro Nome", None)
            st.session_state["respostas"].pop("Material Porta Pavimento Outro Valor", None)

        if modelo_porta_pav in ["Automática", "Pivotante", "Rampa"]:
            st.session_state["respostas"]["Material Porta Pavimento"] = material_porta_pav
        else:
            st.session_state["respostas"].pop("Material Porta Pavimento", None)

        if modelo_porta_pav == "Automática":
            st.session_state["respostas"]["Folhas Porta Pavimento"] = folhas_porta_pav
        else:
            st.session_state["respostas"].pop("Folhas Porta Pavimento", None)

        st.session_state["respostas"]["Altura Porta Pavimento"] = altura_porta_pav
        st.session_state["respostas"]["Largura Porta Pavimento"] = largura_porta_pav

        st.switch_page("pages/4_cabine.py")
        st.rerun()

if __name__ == "__main__":
     portas()
