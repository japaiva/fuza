from sqlalchemy import create_engine, Column, Integer, String, Float, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt

Base = declarative_base()
engine = create_engine('sqlite:///app.db') 
Session = sessionmaker(bind=engine)

# Classes
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    nivel = Column(String)  # 'admin', 'engenharia', ou 'vendedor'

# Classes
class Custos(Base):  
    __tablename__ = 'custos'
    id = Column(Integer, primary_key=True)
    componente = Column(String, nullable=False)
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
    #print("Banco de dados inicializado.")
    #else:
    #    try:
    #        migrate_add_nivel()
    #    except Exception as e:
    #        print(f"Erro durante a migração: {e}")
    #        print("Recriando a tabela 'usuarios'...")
    #        recreate_users_table()
    
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
    custos = session.query(Custos).all()
    session.close()
    return custos

def add_custo(componente, valor):
    session = Session()
    novo_custo = Custos(componente=componente, valor=valor)
    session.add(novo_custo)
    session.commit()
    session.close()

def update_custo(custo_id, componente, valor):
    session = Session()
    custo = session.query(Custos).filter_by(id=custo_id).first()
    if custo:
        custo.componente = componente
        custo.valor = valor
        session.commit()
    session.close()

def remove_custo(custo_id):
    session = Session()
    custo = session.query(Custos).filter_by(id=custo_id).first()
    if custo:
        session.delete(custo)
        session.commit()
    session.close()

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

