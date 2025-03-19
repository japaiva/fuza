import os
from sqlalchemy import create_engine, Column, Integer, String, Float, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import bcrypt

load_dotenv()
Base = declarative_base()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ ERRO: A variável DATABASE_URL não está definida!")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Classes
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    nivel = Column(String)  # 'admin', 'engenharia', ou 'vendedor'

class Custos(Base):  
    __tablename__ = 'custos'
    codigo = Column(String(4), primary_key=True)
    descricao = Column(String(50), nullable=False)
    unidade = Column(String(10), nullable=False)
    valor = Column(Float, nullable=False)

class Parametros(Base):
    __tablename__ = 'parametros'
    id = Column(Integer, primary_key=True)
    parametro = Column(String, nullable=False)
    valor = Column(Float, nullable=False)

# Funçoes para iniciar e atualizar banco de dados

def init_db():
    inspector = inspect(engine)
    if not inspector.has_table('usuarios'):
        Base.metadata.create_all(engine)
    
    # Recria a tabela de custos
    Base.metadata.drop_all(engine, tables=[Custos.__table__])
    Base.metadata.create_all(engine, tables=[Custos.__table__])
    
    add_admin_if_not_exists()


def init_db():
    inspector = inspect(engine)
    
    # Cria a tabela de usuários se não existir
    if not inspector.has_table('usuarios'):
        Base.metadata.create_all(engine, tables=[Usuario.__table__])
    
    # Cria a tabela de custos se não existir
    if not inspector.has_table('custos'):
        Base.metadata.create_all(engine, tables=[Custos.__table__])
    
    # Cria a tabela de parâmetros se não existir
    if not inspector.has_table('parametros'):
        Base.metadata.create_all(engine, tables=[Parametros.__table__])
    
    add_admin_if_not_exists()

def migrate_add_nivel():
    # Verifica se a coluna 'nivel' já existe
    if not hasattr(Usuario, 'nivel'):
        # Adiciona a coluna 'nivel' à tabela 'usuarios'
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN nivel STRING"))
        
        # Atualiza o modelo SQLAlchemy
        Usuario.nivel = Column(String)

    # Atualiza os usuários existentes
    session = Session()
    usuarios = session.query(Usuario).all()
    for usuario in usuarios:
        if not usuario.nivel:
            # Se o usuário for 'admin', mantém como admin, caso contrário, define como 'vendedor'
            usuario.nivel = 'admin' if usuario.username == 'admin' else 'vendedor'
    session.commit()
    session.close()

    print("Migração concluída: coluna 'nivel' adicionada e usuários atualizados.")

def recreate_users_table():
    Base.metadata.drop_all(engine, tables=[Usuario.__table__])
    Base.metadata.create_all(engine, tables=[Usuario.__table__])
    print("Tabela 'usuarios' recriada.")

def add_admin_if_not_exists():
    with Session() as session:
        admin = session.query(Usuario).filter_by(username='admin').first()
        if not admin:
            hashed_password = hash_password('fuza123')
            novo_admin = Usuario(username='admin', password=hashed_password, nivel='admin')
            session.add(novo_admin)
            session.commit()
            print("Usuário admin criado.")
        elif not admin.nivel:
            admin.nivel = 'admin'
            session.commit()
            print("Nível do usuário admin atualizado.")

# Funcoes de busca
def get_user(username):
    session = Session()
    user = session.query(Usuario).filter_by(username=username).first()
    session.close()
    return user

def get_custo(custo_id):
    session = Session()
    custo = session.query(Custos).filter_by(id=custo_id).first()
    session.close()
    return custo

def get_parametro(parametro_id):
    session = Session()
    custo = session.query(Parametros).filter_by(id=parametro_id).first()
    session.close()
    return custo


# Funcoes internas

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())



# -- Funções CRUD de usuarios --

def get_all_users():
    session = Session()
    usuarios = session.query(Usuario).all()
    session.close()
    return usuarios

def add_user(username, password, nivel):
    session = Session()
    hashed_password = hash_password(password)
    novo_usuario = Usuario(
        username=username,
        password=hashed_password,
        nivel=nivel
    )
    session.add(novo_usuario)
    session.commit()
    session.close()

def update_user(old_username, new_username, new_password, nivel):
    session = Session()
    user = session.query(Usuario).filter_by(username=old_username).first()
    if not user:
        session.close()
        return False

    if new_username.strip():
        user.username = new_username.strip()
    if new_password.strip():
        user.password = hash_password(new_password.strip())
    user.nivel = nivel
    session.commit()
    session.close()
    return True

def remove_user(username):
    """
    Remove um usuário do BD.
    """
    session = Session()
    user = session.query(Usuario).filter_by(username=username).first()
    if user:
        session.delete(user)
        session.commit()
    session.close()

# -- Funções CRUD de custos --

def get_all_custos():
    session = Session()
    custos = session.query(Custos).order_by(Custos.codigo).all()
    session.close()
    return custos

def add_custo(codigo, descricao, unidade, valor):
    session = Session()
    novo_custo = Custos(codigo=codigo, descricao=descricao, unidade=unidade, valor=valor)
    session.add(novo_custo)
    session.commit()
    session.close()

def update_custo(codigo, descricao, unidade, valor):
    session = Session()
    custo = session.query(Custos).filter_by(codigo=codigo).first()
    if custo:
        custo.descricao = descricao
        custo.unidade = unidade
        custo.valor = valor
        session.commit()
    session.close()

def remove_custo(codigo):
    session = Session()
    custo = session.query(Custos).filter_by(codigo=codigo).first()
    if custo:
        session.delete(custo)
        session.commit()
    session.close()

def get_custo(codigo):
    session = Session()
    custo = session.query(Custos).filter_by(codigo=codigo).first()
    session.close()
    return custo

# -- Funções CRUD de parametros --

def get_all_parametros():
    session = Session()
    custos = session.query(Parametros).all()
    session.close()
    return custos

def add_parametro(parametro, valor):
    session = Session()
    novo_parametro = Parametros(parametro=parametro, valor=valor)
    session.add(novo_parametro)
    session.commit()
    session.close()

def update_parametro(parametro_id, novo_parametro, novo_valor):
    session = Session()
    parametro = session.query(Parametros).filter_by(id=parametro_id).first()
    if parametro:
        parametro.parametro = novo_parametro
        parametro.valor = novo_valor
        session.commit()
    session.close()

def remove_parametro(parametro_id):
    session = Session()
    parametro = session.query(Parametros).filter_by(id=parametro_id).first()
    if parametro:
        session.delete(parametro)
        session.commit()
    session.close()

def inserir_produtos_iniciais(session):
    produtos = [
        ("CH01", "Chapa Inox 304  1,2 mm", "qtd", 0, "3,00 x 1,20"),
        ("CH02", "Chapa Inox 430 1,2 mm", "qtd", 0, "3,00 x 1,20"),
        ("CH03", "Chapa Galvanizada 1,2 mm", "qtd", 0, "3,00 x 1,20"),
        ("CH04", "Chapa Antiderrapante 1,2 mm", "qtd", 0, "3,00 x 1,20"),
        ("CH05", "Chapa Xadrez 1,2 mm", "qtd", 0, "3,00 x 1,20"),
        ("CH06", "Chapa Pintada 1,2 mm", "qtd", 0, "3,00 x 1,20"),
        ("CH07", "Chapa Aluminio 1,2 mm", "qtd", 0, "3,00 x 1,20"),
        ("FE01", "Parafuso e conjunto 1/4'", "qtd", 0, ""),
        ("FE02", "Parafuso e conjunto 1/5'", "qtd", 0, ""),
        ("FE03", "Tubo Metal", "qtd", 0, "30 x 30"),
        ("PE01", "Travessa 3mm", "qtd comp", 0, ""),
        ("PE02", "Travessa 4mm", "qtd comp", 0, ""),
        ("PE03", "Travessa 6mm", "qtd comp", 0, ""),
        ("PE04", "Longarina 3mm", "qtd comp", 0, ""),
        ("PE05", "Longarina 4mm", "qtd comp", 0, ""),
        ("PE06", "Longarina 6mm", "qtd comp", 0, ""),
        ("PE07", "Perfil Interno 3mm", "qtd comp", 0, ""),
        ("PE08", "Perfil Interno 4mm", "qtd comp", 0, ""),
        ("PE09", "Perfil Interno 6mm", "qtd comp", 0, ""),
        ("PE10", "Perfil Externo 3mm", "qtd comp", 0, ""),
        ("PE11", "Perfil Externo 4mm", "qtd comp", 0, ""),
        ("PE12", "Perfil Externo 6mm", "qtd comp", 0, ""),
        ("PE13", "Polia", "qtd", 0, ""),
        ("PE14", "Cabo aço", "comp", 0, ""),
        ("PE15", "Travessa polia", "qtd comp", 0, ""),
        ("PE16", "Contrapeso pequeno", "qtd", 0, ""),
        ("PE17", "Contrapeso especial", "qtd", 0, ""),
        ("PE18", "Contrapeso grande", "qtd", 0, ""),
        ("PE19", "Pedra pequena", "qtd", 0, "45 kg"),
        ("PE20", "Pedra grande", "qtd", 0, "75 kg"),
        ("PE21", "Guia elevador", "qtd", 0, "5m"),
        ("PE22", "Suporte Guia", "qtd", 0, ""),
        ("PE23", "Guia Contrapeso", "qtd", 0, ""),
        ("PE24", "Suporte Guia Contrapeso", "qtd", 0, ""),
        ("CC01", "Luminaria", "qtd", 0, ""),
        ("CC02", "Ventilador", "qtd", 0, ""),
        ("MO01", "Cilindro Hidraulico", "unid", 0, ""),
    ]

    for codigo, descricao, unidade, valor, obs in produtos:
        stmt = text("""
            INSERT INTO custos (codigo, descricao, unidade, valor)
            VALUES (:codigo, :descricao, :unidade, :valor)
            ON CONFLICT (codigo) DO UPDATE 
            SET descricao = :descricao, unidade = :unidade, valor = :valor
        """)
        session.execute(stmt, {"codigo": codigo, "descricao": descricao, "unidade": unidade, "valor": valor})
    
    session.commit()