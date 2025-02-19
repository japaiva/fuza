import streamlit as st
from functions.layout import show_logo
from functions.style import set_custom_style
from functions.auth import check_auth
from functions.page_utils import get_current_page_name

st.set_page_config(page_title="2: Elevador", layout="wide")
set_custom_style()
show_logo()

current_page = get_current_page_name()
if current_page:
    st.session_state['current_page'] = current_page

check_auth()

def passo_elevador():
    st.markdown('<h3 class="stSubheader">Detalhes Elevador</h3>', unsafe_allow_html=True)

    if "respostas" not in st.session_state:
        st.session_state["respostas"] = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        modelos = ["Passageiro", "Carga", "Monta Prato", "Plataforma Acessibilidade"]
        modelo_default = st.session_state["respostas"].get("Modelo do Elevador", modelos[0])
        
        modelo = st.selectbox(
            "Modelo do Elevador:",
            options=modelos,
            index=modelos.index(modelo_default) if modelo_default in modelos else 0,
            key="modelo_elevador"
        )

        if modelo == "Passageiro":
            capacidade = st.number_input(
                "Capacidade (Número de Pessoas):",
                min_value=1,
                max_value=50,
                step=1,
                value=int(st.session_state["respostas"].get("Capacidade", 1)),
                key="capacidade_pessoas"
            )
        else:
            capacidade = st.number_input(
                "Capacidade (em kg):",
                min_value=0.0,
                max_value=10000.0,
                step=10.0,
                value=float(st.session_state["respostas"].get("Capacidade", 100.0)),
                key="capacidade_kg"
            )

        acionamento = st.selectbox(
            "Acionamento:",
            options=["Motor", "Hidráulico", "Carretel"],
            index=["Motor", "Hidráulico", "Carretel"].index(st.session_state["respostas"].get("Acionamento", "Motor")),
            key="acionamento"
        )

        if acionamento in ["Motor", "Carretel"]:
            tracao = st.selectbox(
                "Tração:",
                options=["1x1", "2x1"],
                index=["1x1", "2x1"].index(st.session_state["respostas"].get("Tração", "1x1")),
                key="tracao"
            )

        if acionamento == "Motor":
            contrapeso = st.selectbox(
                "Contrapeso:",
                options=["Traseiro", "Lateral"],
                index=["Traseiro", "Lateral"].index(st.session_state["respostas"].get("Contrapeso", "Traseiro")),
                key="contrapeso"
            )

    with col2:
        altura_poco = st.number_input(
            "Altura do Poço (m):",
            min_value=0.0,
            max_value=100.0,
            step=0.01,
            format="%.2f",
            value=float(st.session_state["respostas"].get("Altura do Poço", 3.0)),
            key="altura_poco"
        )

        largura_poco = st.number_input(
            "Largura do Poço (m):",
            min_value=0.0,
            max_value=10.0,
            step=0.01,
            format="%.2f",
            value=float(st.session_state["respostas"].get("Largura do Poço", 2.0)),
            key="largura_poco"
        )

        comprimento_poco = st.number_input(
            "Comprimento do Poço (m):",
            min_value=0.00,
            max_value=10.0,
            step=0.01,
            format="%.2f",
            value=float(st.session_state["respostas"].get("Comprimento do Poço", 2.0)),
            key="comprimento_poco"
        )

        pavimentos = st.number_input(
            "Pavimentos:",
            min_value=2,
            max_value=100,
            step=1,
            value=int(st.session_state["respostas"].get("Pavimentos", 2)),
            key="pavimentos"
        )

    if st.button("Salvar", key="salvar_elevador"):
        if altura_poco > 0 and largura_poco > 0 and comprimento_poco > 0:
            st.session_state["respostas"]["Modelo do Elevador"] = modelo
            st.session_state["respostas"]["Capacidade"] = capacidade
            st.session_state["respostas"]["Acionamento"] = acionamento
            if acionamento in ["Motor", "Carretel"]:
                st.session_state["respostas"]["Tração"] = tracao
            if acionamento == "Motor":
                st.session_state["respostas"]["Contrapeso"] = contrapeso
            st.session_state["respostas"]["Altura do Poço"] = altura_poco
            st.session_state["respostas"]["Largura do Poço"] = largura_poco
            st.session_state["respostas"]["Comprimento do Poço"] = comprimento_poco
            st.session_state["respostas"]["Pavimentos"] = pavimentos

            st.switch_page("pages/3_cabine.py")
            st.rerun()
        else:
            st.error("As dimensões do poço devem ser maiores que zero.")

if __name__ == "__main__":
    passo_elevador()