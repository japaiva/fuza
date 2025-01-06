import streamlit as st
from functions.layout import show_logo, set_page_config
from functions.style import set_custom_style

st.set_page_config(page_title="3: Cabine e Corpo", layout="wide")
set_custom_style()
show_logo()

def cabine_corpo():
    st.markdown('<h3 class="stSubheader">Detalhes da Cabine</h3>', unsafe_allow_html=True)

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
                options=["304", "420", "430"],
                index=["304", "420", "430"].index(st.session_state["respostas"].get("Tipo de Inox", "304")),
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

        saida = st.selectbox(
            "Saída:",
            options=["Padrão", "Oposta"],
            index=["Padrão", "Oposta"].index(st.session_state["respostas"].get("Saída", "Padrão")),
            key="saida"
        )

    with col2:
        tracao = st.selectbox(
            "Tração:",
            options=["1x1", "2x1"],
            index=["1x1", "2x1"].index(st.session_state["respostas"].get("Tração", "1x1")),
            key="tracao"
        )

        contrapeso = st.selectbox(
            "Contrapeso:",
            options=["Traseiro", "Lateral", "Carretel", "Hidráulico"],
            index=["Traseiro", "Lateral", "Carretel", "Hidráulico"].index(st.session_state["respostas"].get("Contrapeso", "Traseiro")),
            key="contrapeso"
        )

        piso = st.selectbox(
            "Piso:",
            options=["Por conta do cliente", "Por conta da empresa"],
            index=["Por conta do cliente", "Por conta da empresa"].index(st.session_state["respostas"].get("Piso", "Por conta do cliente")),
            key="piso"
        )

    if st.button("Salvar", key="salvar_cabine_corpo"):
        st.session_state["respostas"]["Material"] = material
        if material == "Inox":
            st.session_state["respostas"]["Tipo de Inox"] = tipo_inox
        st.session_state["respostas"]["Espessura"] = espessura
        st.session_state["respostas"]["Saída"] = saida
        st.session_state["respostas"]["Tração"] = tracao
        st.session_state["respostas"]["Contrapeso"] = contrapeso
        st.session_state["respostas"]["Piso"] = piso
        st.success("Detalhes da cabine salvos com sucesso!")

if __name__ == "__main__":
    cabine_corpo()
