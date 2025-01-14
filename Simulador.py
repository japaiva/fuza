import streamlit as st
from functions.layout import show_logo, set_page_config
from functions.style import set_custom_style
from functions.helpers import calcula_custo_elevador, calcular_dimensoes_cabine, explicacao_calculo

def agrupar_respostas_por_pagina(respostas):
    paginas = {
        "Cliente": ["Solicitante", "Empresa", "Telefone", "Email"],
        "Elevador": ["Modelo do Elevador", "Capacidade", "Pavimentos", "Largura do Poço", "Comprimento do Poço"],
        "Cabine": ["Material", "Tipo de Inox", "Espessura", "Saída", "Altura da Cabine", "Tração", "Contrapeso", "Piso"],  # Adicionado "Altura da Cabine"
        "Porta Cabine": ["Modelo Porta", "Material Porta", "Tipo de Inox Porta", "Folhas Porta", "Altura Porta", "Largura Porta"],
        "Porta Pavimento": ["Modelo Porta Pavimento", "Material Porta Pavimento", "Tipo de Inox Porta Pavimento", "Folhas Porta Pavimento", "Altura Porta Pavimento", "Largura Porta Pavimento"]
    }
    
    respostas_agrupadas = {}
    for pagina, campos in paginas.items():
        respostas_pagina = {campo: respostas.get(campo, "N/A") for campo in campos if campo in respostas}
        if respostas_pagina:
            respostas_agrupadas[pagina] = respostas_pagina
    
    return respostas_agrupadas

def main():
    st.set_page_config(
        page_title="SCP Fuza Elevadores",
        layout="wide"
    )
    set_custom_style()
    show_logo()

    st.markdown('<h2 class="big-title">Simulador de Custos de Projeto</h2>', unsafe_allow_html=True)
    st.markdown("---")

    if "respostas" not in st.session_state:
        st.session_state["respostas"] = {}

    respostas = st.session_state["respostas"]
    respostas_agrupadas = agrupar_respostas_por_pagina(respostas)
    
    paginas = ["Cliente", "Elevador", "Cabine", "Porta Cabine", "Porta Pavimento"]
    paginas_preenchidas = list(respostas_agrupadas.keys())

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Configurações")
        if not respostas:
            st.info("Preencha as etapas nas páginas laterais para começar a simulação.")
        else:
            for pagina, dados in respostas_agrupadas.items():
                st.markdown(f"**{pagina}:** {', '.join([f'{chave}: {valor}' for chave, valor in dados.items()])}")

    with col2:
        st.markdown("#### Resultado Calculado")
        if len(paginas_preenchidas) < len(paginas):
            paginas_faltantes = set(paginas) - set(paginas_preenchidas)
            st.warning(f"Faltam informações das seguintes páginas: {', '.join(paginas_faltantes)}.")
        else:
            modelo = respostas.get("Modelo do Elevador", "N/A")
            capacidade = float(respostas.get("Capacidade", 0))
            pavimentos = int(respostas.get("Pavimentos", 2))

            altura, largura, comprimento = calcular_dimensoes_cabine(respostas)
            st.markdown(f"**Dimensões da Cabine:** {altura:.2f}m x {largura:.2f}m x {comprimento:.2f}m")
            
            with st.expander("Clique aqui para ver detalhes do cálculo"):
                st.markdown(explicacao_calculo())

            custo_est = calcula_custo_elevador(capacidade, pavimentos)
            st.markdown(f"O custo estimado para o modelo **{modelo}** é de:")
            st.markdown(f"<h3 class='custo'>R${custo_est:,.2f}</h3>", unsafe_allow_html=True)

    if st.button("Iniciar Nova Simulação", key="reiniciar"):
        st.session_state["respostas"] = {}
        st.switch_page("pages/1_cliente.py")
        st.rerun()

if __name__ == "__main__":
    main()