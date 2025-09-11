from src.config.bd_config import User, get_session 
from sqlalchemy.exc import IntegrityError

class User_CRUD:

    def __init__(self):
        pass

    # Função para inserir um novo usuário
    def inserir_usuario(self, nome, nickname, email, senha_plana, role):
        # Criação de um novo usuário
        user = User(
            nome=nome,
            nickname=nickname,
            email=email,
            senha=senha_plana, 
            role = role
        )

        # Inserir no banco de dados
        with get_session() as db:
            db.add(user)  
            db.commit()   
            print("Usuário inserido com sucesso!")

    def buscar_usuario_por_nick(self, nick):
        with get_session() as db:
            user = db.query(User).filter(User.nickname == nick).one_or_none()
            if user is None:
                print("Usuário não encontrado.")
                return
            return user
        
    def buscar_usuario_por_email(self, email_search):
        with get_session() as db:
            user = db.query(User).filter(User.email == email_search).one_or_none()
            if user is None:
                print("Usuário não encontrado.")
                return
            return user
        
    def remover_usuario(self, nick):
        with get_session() as db:
            user = db.query(User).filter(User.nickname == nick).one_or_none()
            if user is None:
                print("Usuário não encontrado.")
                return
            db.delete(user)
            return f"Usuário de nick {nick} removido com sucesso."
        
    def listar_usuarios(self):
        with get_session() as db:
            return(
                db.query(User).order_by(User.nome.asc()).offset(offset=0).limit(50).all()
            )
        
    def atualizar_senha(self, nick : str, senha_atual : str, senha_nova : str):
        with get_session() as db:
            user = db.query(User).filter(User.nickname == nick).one_or_none()
            if user is None:
                print("Usuário não encontrado.")
                return
            if not user.verificar_senha(senha_atual):
                print("Senha atual incorreta.")
                return
            user.senha = senha_nova
            print("Senha atualizada com sucesso.")
            return

    def atualizar_dados(self, nick : str, nome_novo : str = None, email_novo : str = None):
        try:
            with get_session() as db:
                user = db.query(User).filter(User.nickname == nick).one_or_none()
                if user is None : return "Usuário não encontrado"
                if email_novo:
                    existing_user = db.query(User).filter(User.email == email_novo).one_or_none()
                    if existing_user:
                        return print(f"Erro: O email {email_novo} já está em uso.")
                if nome_novo is not None: user.nome = nome_novo
                if email_novo is not None: user.email = email_novo
                print("Dados atualizados com sucesso.")
                db.commit()
                return
        except IntegrityError as e:
            print(f"Erro de integridade capturado: {e.orig}")
            db.rollback()
            return
        
        except Exception as e:
            db.rollback()
            print(f"Erro inesperado: {e}")
            return
