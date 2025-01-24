# fuza
Simulador Calculo Projeto

Estrutura Arquivos
.
├── Simulador.py                # Arquivo principal (entry point)
├── config.yaml                 # Arquivo de config do YAML
├── requirements.txt            # Dependências (ex.: Streamlit, SQLAlchemy, bcrypt, PyYAML, etc.)
├── assets/
│    └── logo.png
├── functions/
│    ├── __init__.py
│    ├── admin.py               # Funções específicas de administração (admin_page, etc.)
│    ├── auth.py                # Todas as funções de autenticação / login / checagem
│    ├── database.py            # Funções (ORM) e modelos do banco de dados
│    ├── helpers.py             # Funções gerais de cálculo/validação
│    ├── layout.py              # Funções relacionadas a layout (logo, estilo, etc.)
│    ├── style.py               # CSS e estilos customizados
│    └── page_utils.py          # Utilidades para as páginas (ex.: get_current_page_name)
├── pages/
│    ├── 1_cliente.py
│    ├── 2_elevador.py
│    ├── 3_cabine.py
│    ├── 4_porta_cabine.py
│    └── 5_porta_pavimento.py
└── usuarios.db                 # Banco de dados SQLite

