import streamlit as st
from functions.layout import show_logo
from functions.style import set_custom_style
from functions.auth import check_auth
from functions.page_utils import get_current_page_name
from functions.calc import calcular_dimensionamento_completo  # Importa o cálculo das dimensões

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

    # Criação de 3 colunas para organizar os campos
    col1, col2, col3 = st.columns(3)

    # Coluna 1: Material e Espessura
    with col1:
        material_options = ["Inox 430", "Inox 304", "Chapa Pintada", "Alumínio", "Outro"]
        material_default = st.session_state["respostas"].get("Material", "Inox 430")
        material = st.selectbox(
            "Material:",
            options=material_options,
            index=material_options.index(material_default) if material_default in material_options else 0,
            key="material"
        )

        # Definir opções de espessura baseadas no material selecionado
        espessura_options = {
            "Inox 430": ["1,2", "1,5"],
            "Inox 304": ["1,2", "1,5"],
            "Chapa Pintada": ["1,2", "1,5"],
            "Alumínio": ["1,2", "2,0"],
            "Outro": None  # Não exibir espessura para "Outro"
        }

        if material == "Outro":
            outro_nome = st.text_input(
                "Nome do Material:",
                value=st.session_state["respostas"].get("Material Outro Nome", ""),
                key="material_outro_nome"
            )
            outro_valor = st.number_input(
                "Valor do Material:",
                min_value=0.0,
                value=float(st.session_state["respostas"].get("Material Outro Valor", 0.0)),
                step=0.1,
                key="material_outro_valor"
            )
        else:
            espessura_default = st.session_state["respostas"].get("Espessura", "1,2")
            espessura = st.selectbox(
                "Espessura (mm):",
                options=espessura_options[material],
                index=espessura_options[material].index(espessura_default) if espessura_default in espessura_options[material] else 0,
                key="espessura"
            )

    # Coluna 2: Saída e Material do Piso
    with col2:
        # Obtém a escolha atual do contrapeso
        contrapeso_atual = st.session_state["respostas"].get("Contrapeso", "Lateral")

        # Opções de saída, removendo "Oposta" se contrapeso for "Traseiro"
        opcoes_saida = ["Padrão", "Oposta"]
        if contrapeso_atual == "Traseiro":
            opcoes_saida.remove("Oposta")

        # Guarda o valor anterior da saída
        saida_anterior = st.session_state["respostas"].get("Saída", "Padrão")

        saida = st.selectbox(
            "Saída:",
            options=opcoes_saida,
            index=opcoes_saida.index(st.session_state["respostas"].get("Saída", "Padrão")),
            key="saida"
        )

        # Se a saída foi alterada, refaz o cálculo
        if saida != saida_anterior:
            st.session_state["respostas"]["Saída"] = saida
            dimensoes, explicacoes = calcular_dimensionamento_completo(st.session_state["respostas"])
            st.session_state["respostas"]["Largura da Cabine"] = dimensoes["cab"]["largura"]
            st.session_state["respostas"]["Comprimento da Cabine"] = dimensoes["cab"]["compr"]
            st.rerun()  # Recarrega a página para refletir os novos valores

        # Piso: Se for por conta da empresa, exibe opções de material
        piso = st.selectbox(
            "Piso:",
            options=["Por conta do cliente", "Por conta da empresa"],
            index=["Por conta do cliente", "Por conta da empresa"].index(st.session_state["respostas"].get("Piso", "Por conta do cliente")),
            key="piso"
        )

        if piso == "Por conta da empresa":
            material_piso_options = ["Antiderrapante", "Outro"]
            material_piso_default = st.session_state["respostas"].get("Material Piso Cabine", "Antiderrapante")

            material_piso = st.selectbox(
                "Material do Piso da Cabine:",
                options=material_piso_options,
                index=material_piso_options.index(material_piso_default) if material_piso_default in material_piso_options else 0,
                key="material_piso"
            )

            if material_piso == "Outro":
                outro_nome_piso = st.text_input(
                    "Nome do Material do Piso:",
                    value=st.session_state["respostas"].get("Material Piso Outro Nome", ""),
                    key="material_piso_outro_nome"
                )
                outro_valor_piso = st.number_input(
                    "Valor do Material do Piso:",
                    min_value=0.0,
                    value=float(st.session_state["respostas"].get("Material Piso Outro Valor", 0.0)),
                    step=0.1,
                    key="material_piso_outro_valor"
                )

    # Coluna 3: Dimensões calculadas e Altura da Cabine
    with col3:
        dimensoes, explicacoes = calcular_dimensionamento_completo(st.session_state["respostas"])
        largura_calculada = dimensoes["cab"]["largura"]
        comprimento_calculado = dimensoes["cab"]["compr"]

        st.number_input("Largura da Cabine (m):", value=largura_calculada, disabled=True, key="largura_cabine_calculada")
        st.number_input("Comprimento da Cabine (m):", value=comprimento_calculado, disabled=True, key="comprimento_cabine_calculado")

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

    # Botão Salvar
    if st.button("Salvar", key="salvar_cabine_corpo"):
        st.session_state["respostas"]["Material"] = material
        if material == "Outro":
            st.session_state["respostas"]["Material Outro Nome"] = outro_nome
            st.session_state["respostas"]["Material Outro Valor"] = outro_valor
        elif "Material Outro Nome" in st.session_state["respostas"]:
            del st.session_state["respostas"]["Material Outro Nome"]
            del st.session_state["respostas"]["Material Outro Valor"]

        if material != "Outro":
            st.session_state["respostas"]["Espessura"] = espessura

        st.session_state["respostas"]["Saída"] = saida
        st.session_state["respostas"]["Altura da Cabine"] = altura_cabine
        st.session_state["respostas"]["Piso"] = piso

        if piso == "Por conta da empresa":
            st.session_state["respostas"]["Material Piso Cabine"] = material_piso
            if material_piso == "Outro":
                st.session_state["respostas"]["Material Piso Outro Nome"] = outro_nome_piso
                st.session_state["respostas"]["Material Piso Outro Valor"] = outro_valor_piso

        st.switch_page("Simulador.py")
        st.rerun()

if __name__ == "__main__":
    cabine_corpo()

