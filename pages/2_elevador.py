import streamlit as st
from functions.layout import show_logo, set_page_config
from functions.style import set_custom_style

st.set_page_config(page_title="2: Elevador", layout="wide")
set_custom_style()
show_logo()

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

        pavimentos = st.number_input(
            "Pavimentos:",
            min_value=2,
            max_value=100,
            step=1,
            value=int(st.session_state["respostas"].get("Pavimentos", 2)),
            key="pavimentos"
        )

    with col2:
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

    if st.button("Salvar", key="salvar_elevador"):
        if largura_poco > 0 and comprimento_poco > 0:
            st.session_state["respostas"]["Modelo do Elevador"] = modelo
            st.session_state["respostas"]["Capacidade"] = capacidade
            st.session_state["respostas"]["Pavimentos"] = pavimentos
            st.session_state["respostas"]["Largura do Poço"] = largura_poco
            st.session_state["respostas"]["Comprimento do Poço"] = comprimento_poco

            st.switch_page("pages/3_cabine.py")
            st.rerun()
        else:
            st.error("A largura e o comprimento do poço devem ser maiores que zero.")

if __name__ == "__main__":
    passo_elevador()