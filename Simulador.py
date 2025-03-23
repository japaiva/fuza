import streamlit as st
import yaml
from yaml.loader import SafeLoader
from functions.calc import calcular_dimensionamento_completo, calcular_componentes
from functions.pdf_utils import gerar_pdf_demonstrativo
from functions.database import init_db, get_all_users
from functions.auth import verify_login
from functions.layout import show_logo
from functions.style import set_custom_style
from functions.helpers import agrupar_respostas_por_pagina
from functions.admin import usuarios_page, custos_page,parametros_page

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

def format_number(value):
    return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

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
        paginas = ["Cliente", "Elevador", "Cabine", "Portas"]
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
                        itens_formatados = []
                        
                        # Separação personalizada dentro de 'Portas'
                        if pagina == "Portas":
                            portas_cabine = []
                            portas_pavimento = []
                            
                            for chave, valor in dados.items():
                                if "Pavimento" in chave:
                                    portas_pavimento.append(f"**{chave}**: {valor}")
                                else:
                                    portas_cabine.append(f"**{chave}**: {valor}")

                            # Adiciona título antes de cada categoria
                            if portas_cabine:
                                itens_formatados.append("##### Portas de Cabine")
                                itens_formatados.extend(portas_cabine)

                            if portas_pavimento:
                                itens_formatados.append("\n##### Portas de Pavimento")
                                itens_formatados.extend(portas_pavimento)

                        else:
                            # Para outras páginas, apenas formatar os itens normalmente
                            itens_formatados = [f"**{chave}**: {valor}" for chave, valor in dados.items()]

                        # Monta a string com quebras de linha
                        final_str = "\n".join(itens_formatados)
                        st.markdown(final_str)

        # ---------------------------------------------
        # COLUNA 2: Resultado / Cálculo
        # ---------------------------------------------
        with col2:
            dimensionamento, explicacao = calcular_dimensionamento_completo(respostas)
            st.markdown("#### Cálculos")
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

                        componentes, custos, custo_total, todos_custos = calcular_componentes(dimensionamento, respostas)

                        # Agrupar componentes
                        grupos = {}
                        for codigo, info in componentes.items():
                            grupo = info['grupo']
                            subgrupo = info['subgrupo']
                            if grupo not in grupos:
                                grupos[grupo] = {}
                            if subgrupo not in grupos[grupo]:
                                grupos[grupo][subgrupo] = []
                            grupos[grupo][subgrupo].append(info)

                        # Exibir componentes
                        for grupo, subgrupos in grupos.items():
                            st.markdown(f"##### {grupo}")
                            for subgrupo, itens in subgrupos.items():
                                #st.markdown(f"#### {subgrupo}")
                                for item in itens:
                                    formatted_unit_cost = format_number(item['custo_unitario'])
                                    formatted_total_cost = format_number(item['custo_total'])
                                    line = (
                                        f"**{item['descricao']}** ({item['codigo']}) - "
                                        f"{item['quantidade']} {item['unidade']}, "
                                        f"Custo Unitário: {formatted_unit_cost}, "
                                        f"Custo Total: {formatted_total_cost}, "
                                        f"Cálculo: {item['explicacao']}"
                                    )
                                    st.markdown(line)

                        st.markdown(f"**Custo Total: {format_number(custo_total)}**")
                        
                    with st.expander("Composição Preço", expanded=False):
                        st.info("Conteúdo não disponível.")
                    
                # Exibe custo final
                st.markdown(f"O custo estimado para este modelo é de:")
                st.markdown(f"<h3 class='custo'>R$ {custo_total:,.2f}</h3>", unsafe_allow_html=True)
                
                if nivel != 'vendedor':
                    st.markdown(" ")

                    # Criando duas colunas com o mesmo tamanho
                    col1, col2 = st.columns(2)

                    # Criando uma variável para armazenar o PDF gerado
                    pdf_bytes = None

                    # Botão para gerar o PDF na primeira coluna
                    with col1:
                        gerar_pdf = st.button("Gerar PDF", use_container_width=True)

                    # Se o usuário clicar, geramos o PDF
                    if gerar_pdf:
                        componentes, custos, custo_total, todos_custos = calcular_componentes(dimensionamento, respostas)
                        respostas_agrupadas = agrupar_respostas_por_pagina(respostas)
                        
                        grupos = {}
                        for codigo, info in componentes.items():
                            grupo = info['grupo']
                            subgrupo = info['subgrupo']
                            if grupo not in grupos:
                                grupos[grupo] = {}
                            if subgrupo not in grupos[grupo]:
                                grupos[grupo][subgrupo] = []
                            grupos[grupo][subgrupo].append(info)
                        
                        pdf_bytes = gerar_pdf_demonstrativo(
                            dimensionamento,
                            explicacao,
                            componentes,
                            custo_total,
                            respostas,
                            respostas_agrupadas,
                            grupos
                        )

                    # Botão de download na segunda coluna (aparece apenas se o PDF foi gerado)
                    with col2:
                        if pdf_bytes:
                            st.download_button(
                                label="Baixar PDF",
                                data=pdf_bytes,
                                file_name="relatorio_calculo.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )

                    # Botão 2 - Proposta Comercial
                    #if st.button("Gerar Proposta Comercial"):
                    #    # Precisamos das respostas agrupadas para exibir no PDF
                    #    from functions.helpers import agrupar_respostas_por_pagina
                    #    respostas_agrupadas = agrupar_respostas_por_pagina(respostas)
                    #    
                    #    nome_cliente = respostas.get("Solicitante", "Cliente")
                    #    
                    #    pdf_bytes = gerar_pdf_proposta_comercial(
                    #       dimensionamento,
                    #       componentes_formatados,
                    #       custo_total,
                    #       respostas_agrupadas,
                    #        nome_cliente
                    #    )
                    #    st.download_button(
                    #        label="Baixar Proposta Comercial",
                    #        data=pdf_bytes,
                    #        file_name="proposta_comercial.pdf",
                    #        mime="application/pdf"
                    #    )    
        
        st.markdown("---")

        if st.button("Iniciar Nova Simulação", key="reiniciar"):
            st.session_state["respostas"] = {}
            st.switch_page("pages/1_cliente.py")
            st.rerun()

if __name__ == "__main__":
    main()
