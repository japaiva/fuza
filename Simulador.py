import streamlit as st
import yaml
from yaml.loader import SafeLoader
import math 
from functions.database import init_db, add_admin_if_not_exists, get_all_users, get_user
from functions.auth import verify_login, check_auth
from functions.layout import show_logo
from functions.style import set_custom_style
from functions.helpers import calcula_custo_elevador, calcular_dimensoes_cabine, dem_dimensao,  calcular_chapas_cabine, dem_placas
from functions.admin import usuarios_page, custos_page, parametros_page

st.set_page_config(
    page_title="SCP - Fuza Elevadores",
    layout="wide"
)

# Inicializa DB e garante que exista o admin
init_db()

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

        paginas = ["Cliente", "Elevador", "Cabine", "Porta Cabine", "Porta Pavimento"]
        paginas_preenchidas = list(respostas_agrupadas.keys())

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Configurações")
            if not respostas:
                st.info("Preencha as etapas nas páginas laterais para começar a simulação.")
            else:
                for pagina, dados in respostas_agrupadas.items():
                    campos_str = ", ".join([f"{chave}: {valor}" for chave, valor in dados.items()])
                    st.markdown(f"**{pagina}:** {campos_str}")

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
                st.markdown(f"**Dimensões Cabine:** {largura:.2f}m L x {comprimento:.2f}m C x {altura:.2f}m A")
                
                if nivel != 'vendedor':
                    with st.expander("Detalhes do cálculo da dimensão da cabine"):
                        st.markdown(dem_dimensao(respostas))     

                    with st.expander("Detalhes do cálculo de necessidade de chapas"):
                        chapas_info = calcular_chapas_cabine(altura, largura, comprimento)
                        
                        if isinstance(chapas_info, str):
                            st.error(chapas_info)
                        else:
                            st.markdown(dem_placas(chapas_info))

                    custo_est = calcula_custo_elevador(capacidade, pavimentos)
                    st.markdown(f"O custo estimado para este modelo é de:")
                    st.markdown(f"<h3 class='custo'>R${custo_est:,.2f}</h3>", unsafe_allow_html=True)

        st.markdown("---")

        if st.button("Iniciar Nova Simulação", key="reiniciar"):
            st.session_state["respostas"] = {}
            st.switch_page("pages/1_cliente.py")
            st.rerun()

def agrupar_respostas_por_pagina(respostas):
    """Agrupa as respostas de acordo com cada página, para exibir no resumo."""
    def get_unidade(campo, valor, modelo):
        unidades = {
            "Capacidade": "pessoas" if "passageiro" in modelo.lower() else "kg",
            "Pavimentos": "",
            "Largura do Poço": "m",
            "Comprimento do Poço": "m",
            "Altura da Cabine": "m",
            "Espessura": "mm",
            "Altura Porta": "m",
            "Largura Porta": "m",
            "Altura Porta Pavimento": "m",
            "Largura Porta Pavimento": "m"
        }
        return unidades.get(campo, "")

    paginas = {
        "Cliente": ["Solicitante", "Empresa", "Telefone", "Email"],
        "Elevador": ["Modelo do Elevador", "Capacidade", "Pavimentos", "Largura do Poço", "Comprimento do Poço"],
        "Cabine": ["Material", "Tipo de Inox", "Espessura", "Saída", "Altura da Cabine", "Tração", "Contrapeso", "Piso", "Material Piso Cabine"],
        "Porta Cabine": ["Modelo Porta", "Material Porta", "Tipo de Inox Porta", "Folhas Porta", "Altura Porta", "Largura Porta"],
        "Porta Pavimento": ["Modelo Porta Pavimento", "Material Porta Pavimento", "Tipo de Inox Porta Pavimento", 
                            "Folhas Porta Pavimento", "Altura Porta Pavimento", "Largura Porta Pavimento"]
    }
    
    modelo_elevador = respostas.get("Modelo do Elevador", "").lower()
    
    respostas_agrupadas = {}
    for pagina, campos in paginas.items():
        dados_pagina = {}
        for campo in campos:
            if campo in respostas:
                valor = respostas[campo]
                unidade = get_unidade(campo, valor, modelo_elevador)
                if unidade:
                    valor = f"{valor} {unidade}"
                dados_pagina[campo] = valor
        if dados_pagina:
            respostas_agrupadas[pagina] = dados_pagina
    return respostas_agrupadas

if __name__ == "__main__":
    main()
