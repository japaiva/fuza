import streamlit as st
import yaml
from yaml.loader import SafeLoader
import math
from functions.database import init_db, add_admin_if_not_exists, get_all_users, get_user, inserir_produtos_iniciais, Session
from functions.auth import verify_login
from functions.layout import show_logo
from functions.style import set_custom_style

from functions.helpers import (
    agrupar_respostas_por_pagina
)

from functions.calc import (
    calcular_dimensionamento_completo,
    calcular_componentes
)

from functions.admin import (
    usuarios_page, custos_page, 
    parametros_page
)

st.set_page_config(
    page_title="SCP - Fuza Elevadores",
    layout="wide"
)

# Inicializa DB e garante que exista o admin
init_db()

#session = Session()
#inserir_produtos_iniciais(session)
#session.close()

@st.cache_resource
def load_config():
    """Carrega as configurações do arquivo YAML e
       atualiza as credenciais com base no BD de usuários."""
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    # Atualiza o dicionário de 'credentials' com dados do banco
    users = get_all_users()
    credentials = {}
    for user in users:
        credentials[user.username] = {
            "name": user.username,
            "password": user.password,  # já é hash
        }
    config['credentials'] = credentials
    return config

config = load_config()

def main():
    """Função principal do app que gerencia login e redirecionamento das páginas."""
    set_custom_style()
    show_logo()

    st.markdown('<h3 class="stSubheader">Simulador de Custos de Projeto</h3>', unsafe_allow_html=True)

    # Se não estiver autenticado, exibe tela de login
    if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Login")
            st.info("Entre com suas credenciais para acessar o sistema.")

        with col2:
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')

        st.markdown("---")

        if st.button('Login'):
            if verify_login(username, password, config):
                st.session_state['authentication_status'] = True
                st.session_state['username'] = username
                if 'return_to' in st.session_state:
                    return_page = st.session_state['return_to']
                    del st.session_state['return_to']
                    st.switch_page(return_page)
                else:
                    st.rerun()
            else:
                st.session_state['login_error'] = 'Username/password is incorrect'
                st.rerun()

        if 'login_error' in st.session_state:
            st.error(st.session_state['login_error'])
            del st.session_state['login_error']

    else:
        st.sidebar.write(f'Bem-vindo *{st.session_state["username"]}*')
        nivel = st.session_state['nivel']

        # Menu para admin
        if nivel == 'admin':
            admin_option = st.sidebar.selectbox(
                "Funções Administrativas",
                ["Funções Administrativas", "Parâmetros", "Usuários", "Custos"],
                index=0,
                label_visibility="collapsed"
            )

            if admin_option == "Usuários":
                usuarios_page()
                return
            elif admin_option == "Parâmetros":
                parametros_page()
                return
            elif admin_option == "Custos":
                custos_page()
                return

        # Menu para engenharia
        elif nivel == 'engenharia':
            admin_option = st.sidebar.selectbox(
                "Funções Administrativas",
                ["Funções Administrativas", "Custos"],
                index=0,
                label_visibility="collapsed"
            )

            if admin_option == "Custos":
                custos_page()
                return

        if st.sidebar.button('Logout'):
            for key in ['authentication_status', 'username', 'nivel']:
                st.session_state.pop(key, None)
            st.rerun()

        # Se chegou aqui, está logado
        if "respostas" not in st.session_state:
            st.session_state["respostas"] = {}

        respostas = st.session_state["respostas"]
        respostas_agrupadas = agrupar_respostas_por_pagina(respostas)

        # Lista de páginas que devem ser preenchidas
        paginas = ["Cliente", "Elevador", "Cabine", "Porta Cabine", "Porta Pavimento"]
        paginas_preenchidas = list(respostas_agrupadas.keys())

        col1, col2 = st.columns(2)

        # ---------------------------------------------
        # COLUNA 1: exibindo as respostas sem bullets
        # ---------------------------------------------
        with col1:
            st.markdown("#### Configurações")
            if not respostas:
                st.info("Preencha as etapas nas páginas laterais para começar a simulação.")
            else:
                for pagina, dados in respostas_agrupadas.items():
                    with st.expander(pagina, expanded=False):
                        # Monta uma string única separada por vírgulas
                        itens_formatados = [f"**{chave}**: {valor}" for chave, valor in dados.items()]
                        # Junta tudo em uma linha só, separado por vírgula e espaço
                        final_str = ", ".join(itens_formatados)
                        st.markdown(final_str)

        # ---------------------------------------------
        # COLUNA 2: Resultado / Cálculo
        # ---------------------------------------------
        with col2:
            dimensionamento, explicacao = calcular_dimensionamento_completo(respostas)
            st.markdown("#### Resultado Calculado")
            if len(paginas_preenchidas) < len(paginas):
                paginas_faltantes = set(paginas) - set(paginas_preenchidas)
                st.warning(f"Faltam informações das seguintes páginas: {', '.join(paginas_faltantes)}.")
            else:
                # Expander Ficha Técnica
                with st.expander("Ficha Técnica", expanded=False):
                    st.markdown(
                        f"**Dimensões Cabine:** {dimensionamento['cab']['largura']:.2f}m L x "
                        f"{dimensionamento['cab']['compr']:.2f}m C x {dimensionamento['cab']['altura']:.2f}m A"
                    )
                    st.markdown(
                        f"**Capacidade e Tração Cabine**: {dimensionamento['cab']['capacidade']:.2f} kg, "
                        f"{dimensionamento['cab']['tracao']:.2f} kg"
                    )

                # Expanders paralelos (não aninhados)
                if nivel != 'vendedor':
                    with st.expander("Cálculo Dimensionamento", expanded=False):
                        st.markdown(explicacao)

                    with st.expander("Cálculo Componentes", expanded=False):
                        componentes_formatados, custos, custo_total, todos_custos = calcular_componentes(dimensionamento, respostas)
                                
                        # Mapeamento manual dos códigos para os grupos desejados
                        group_mapping = {
                            # Grupo CABINE
                            "CH01": "CABINE", "CH02": "CABINE", "CH06": "CABINE", "CH07": "CABINE", "FE01": "CABINE",
                            
                            # Grupo CARRINHO
                            "PE01": "CARRINHO", "PE02": "CARRINHO", "PE03": "CARRINHO", "PE04": "CARRINHO",
                            "PE05": "CARRINHO", "PE06": "CARRINHO", "FE02": "CARRINHO", "PE07": "CARRINHO",
                            "PE08": "CARRINHO", "PE09": "CARRINHO", "PE10": "CARRINHO", "PE11": "CARRINHO",
                            "PE12": "CARRINHO",
                            
                            # Grupo TRACAO
                            "MO01": "TRACAO", "PE13": "TRACAO", "PE14": "TRACAO", "PE15": "TRACAO",
                            "PE16": "TRACAO", "PE17": "TRACAO", "PE18": "TRACAO", "PE19": "TRACAO",
                            "PE20": "TRACAO", "PE21": "TRACAO", "PE22": "TRACAO", "PE23": "TRACAO",
                            "PE24": "TRACAO",

                            # Grupo SISTEMAS COMPLEMENTARES
                            "CC01": "SISTEMAS COMPLEMENTARES",
                            "CC02": "SISTEMAS COMPLEMENTARES"
                        }
                        
                        # Ordem dos grupos
                        group_order = ["CABINE", "CARRINHO", "TRACAO", "PAVIMENTOS", "SISTEMAS COMPLEMENTARES"]
                        group_items = {group: [] for group in group_order}
                        
                        def format_number(value):
                                return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

                        
                        # Agrupa os itens de acordo com o mapeamento
                        for codigo, info in componentes_formatados.items():
                            grupo = group_mapping.get(codigo, "CABINE")  # Default para CABINE se não mapeado
                            formatted_unit_cost = format_number(info['custo_unitario'])
                            formatted_total_cost = format_number(info['custo_total'])
                            line = (
                                f"**{info['descricao']}** ({codigo}) - "
                                f"{info['quantidade']} {info['unidade']}, "
                                f"Custo Unitário: {formatted_unit_cost}, "
                                f"Custo Total: {formatted_total_cost}, "
                                f"Cálculo: {info['explicacao']}"
                            )
                            group_items[grupo].append(line)
                        
                        # Exibe cada grupo com seu título e itens (se houver)
                        for grupo in group_order:
                            st.markdown(f"###### {grupo}")
                            if group_items[grupo]:
                                for line in group_items[grupo]:
                                    st.markdown(line)
                            else:
                                st.markdown("*Sem itens*")
                        
                    with st.expander("Composição Preço", expanded=False):
                        st.info("Conteúdo não disponível.")
                    
                # Exibe custo final
                st.markdown(f"O custo estimado para este modelo é de:")
                st.markdown(f"<h3 class='custo'>R$ {custo_total:,.2f}</h3>", unsafe_allow_html=True)
        st.markdown("---")

        if st.button("Iniciar Nova Simulação", key="reiniciar"):
            st.session_state["respostas"] = {}
            st.switch_page("pages/1_cliente.py")
            st.rerun()

if __name__ == "__main__":
    main()
