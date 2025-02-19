# functions/admin_functions.py

import streamlit as st
import pandas as pd
from functions.database import (
    get_all_users, add_user, update_user, remove_user, 
    get_all_custos,add_custo,update_custo,remove_custo,
    get_all_parametros,add_parametro,update_parametro,remove_parametro
)

def usuarios_page():
    st.markdown("#### Usuários")
    
    # Lista de usuários existentes
    usuarios = get_all_users()

    # Cria uma lista para o selectbox:
    # O primeiro item é "Novo usuário", depois os nomes dos usuários do BD
    opcoes = ["Novo usuário"] + [u.username for u in usuarios]
    escolha = st.selectbox("Selecione ou crie um usuário", opcoes)       

    # Se for "Novo usuário", o form fica em branco
    if escolha == "Novo usuário":
        edit_username = st.text_input("Username", value="")
        edit_password = st.text_input("Senha", type="password")
        edit_nivel = st.selectbox(
            "Nível", 
            ["admin", "engenharia", "vendedor"], 
            index=2  # Define 'vendedor' como padrão para novos usuários
        )

        # Só faz sentido exibir "Salvar" (para adicionar)
        if st.button("Salvar"):
            if edit_username.strip() and edit_password.strip():
                add_user(edit_username.strip(), edit_password.strip(), edit_nivel)
                st.success("Usuário adicionado com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha username e senha para criar o usuário.")

    else:
        # Se escolheu um usuário existente, localizar no BD
        user_obj = next((u for u in usuarios if u.username == escolha), None)
        if not user_obj:
            st.error("Usuário não encontrado. Talvez tenha sido excluído?")
            st.stop()

        # Preenche os campos com dados do usuário
        edit_username = st.text_input("Username", value=user_obj.username)
        edit_password = st.text_input("Nova senha (em branco para manter)", type="password")
        edit_nivel = st.selectbox(
            "Nível", 
            ["admin", "engenharia", "vendedor"], 
            index=["admin", "engenharia", "vendedor"].index(getattr(user_obj, 'nivel', 'vendedor'))
        )

        if st.button("Salvar"):
            sucesso = update_user(
                old_username=escolha,
                new_username=edit_username,
                new_password=edit_password,
                nivel=edit_nivel
            )
            if sucesso:
                st.success("Usuário atualizado com sucesso!")
            else:
                st.error("Falha ao atualizar (usuário pode não existir).")
            st.rerun()

        # Botão de EXCLUIR => remove_user
        if st.button("Excluir"):
            remove_user(escolha)
            st.success("Usuário removido com sucesso!")
            st.rerun()

def custos_page():
    st.markdown("#### Custos")
    
    # Carrega os custos do BD
    custos = get_all_custos()
    old_df = pd.DataFrame([
        {"codigo": c.codigo, "descricao": c.descricao, "unidade": c.unidade, "valor": c.valor}
        for c in custos
    ])

    # Se não existir nenhum registro, cria colunas para evitar erro
    if old_df.empty:
        old_df = pd.DataFrame(columns=["codigo", "descricao", "unidade", "valor"])

    edited_df = st.data_editor(
        old_df,
        num_rows="dynamic",       
        use_container_width=True,  
        column_config={
            "codigo": st.column_config.TextColumn(
                "Código",
                help="Código alfanumérico de 4 caracteres",
                max_chars=4,
                validate="^[a-zA-Z0-9]{4}$",
                width="small"
            ),
            "descricao": st.column_config.TextColumn(
                "Descrição",
                help="Descrição ou componente",
                max_chars=50,
                width="large"
            ),
            "unidade": st.column_config.TextColumn(
                "Unidade",
                help="Unidade de medida",
                max_chars=10,
                width="small"
            ),
            "valor": st.column_config.NumberColumn(
                "Valor",
                help="Valor do componente",
                min_value=0,
                max_value=1000000,
                step=0.01,
                format="%.2f",
            ),
        }
    )

    if st.button("Salvar Alterações"):
        # Ordena o DataFrame pelo código
        edited_df = edited_df.sort_values(by="codigo")

        # Identifica linhas removidas (old_codigos que não estão mais em new_codigos)
        old_codigos = set(old_df["codigo"])
        new_codigos = set(edited_df["codigo"])
        removed_codigos = old_codigos - new_codigos
        for r_codigo in removed_codigos:
            remove_custo(r_codigo)

        # Identifica linhas criadas ou atualizadas
        for _, row in edited_df.iterrows():
            codigo = row["codigo"]
            descricao = row["descricao"]
            unidade = row["unidade"]
            valor = float(row["valor"]) if row["valor"] else 0.0

            if codigo not in old_codigos:
                # Registro novo
                add_custo(codigo, descricao, unidade, valor)
            else:
                # Registro existente => update
                update_custo(codigo, descricao, unidade, valor)

        st.success("Alterações salvas com sucesso!")
        st.rerun()
        
def parametros_page():
    st.markdown("#### Parâmetros")
    
    # Carrega os parametros do BD
    parametros = get_all_parametros()
    old_df = pd.DataFrame([
        {"id": p.id, "Parâmetro": p.parametro, "Valor": p.valor}
        for p in parametros
    ])

    # Se não existir nenhum registro, cria colunas para evitar erro
    if old_df.empty:
        old_df = pd.DataFrame(columns=["id", "Parâmetro", "Valor"])

    edited_df = st.data_editor(
        old_df,
        num_rows="dynamic",       
        use_container_width=True,  
        column_config={
            "id": st.column_config.Column(
                "ID",
                disabled=True,  # visível mas não editável
                width="small"
            ),
            "Parâmetro": st.column_config.TextColumn(
                "Parâmetro",
                help="Nome do parâmetro",
                max_chars=50,
                width="large"   # deixa maior que o padrão
            ),
            "Valor": st.column_config.NumberColumn(
                "Valor",
                help="Valor do parâmetro",
                min_value=0,
                max_value=1000000,
                step=0.01,
                format="%.2f",
            ),
        }
    )

    if st.button("Salvar Alterações"):
        # Converte a coluna 'id' para int ou None, caso fique em branco
        edited_df["id"] = edited_df["id"].apply(
            lambda x: int(x) if str(x).isdigit() else None
        )

        # Identifica linhas removidas (old_ids que não estão mais em new_ids)
        old_ids = set(old_df["id"].dropna().astype(int))
        new_ids = set(edited_df["id"].dropna().astype(int))
        removed_ids = old_ids - new_ids
        for r_id in removed_ids:
            remove_parametro(r_id)

        # Identifica linhas criadas ou atualizadas
        for _, row in edited_df.iterrows():
            row_id = row["id"]
            parametro = row["Parâmetro"]  # Corrigido aqui
            valor = float(row["Valor"]) if row["Valor"] else 0.0

            if row_id is None:
                # Registro novo
                add_parametro(parametro, valor)
            else:
                # Registro existente => update
                update_parametro(row_id, parametro, valor)

        st.success("Alterações salvas com sucesso!")
        st.rerun()
