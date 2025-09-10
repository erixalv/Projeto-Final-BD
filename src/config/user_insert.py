from bd_config import User, get_session 

# Função para inserir um novo usuário
def inserir_usuario(nome, nickname, email, senha_plana, role):
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

def remover_usuario(nick):
    with get_session() as db:
        user = db.query(User).filter(User.nickname == nick).one_or_none()
        if user is None:
            print("O usuário com esse nick não existe.")
            return
        db.delete(user)
        db.commit()
        print(f"Usuário com nickname {nick} removido com sucesso!")

def buscar_usuario(nick):
    with get_session() as db:
        user = db.query(User).filter(User.nickname == nick).one_or_none()
        if user is None:
            print("Usuário não encontrado.")
            return
        return user
    
def remover_usuario(nick):
    with get_session() as db:
        user = db.query(User).filter(User.nickname == nick).one_or_none()
        if user is None:
            print("Usuário não encontrado.")
            return
        db.delete(user)
        return f"Usuário de nick {nick} removido com sucesso."
    
def listar_usuarios():
    with get_session() as db:
        return(
            db.query(User).order_by(User.nome.asc()).offset(offset=0).limit(50).all()
        )
    
def atualizar_senha():
    return

def atualizar_nick():
    return

#inserir_usuario('Maria Thereza', 'maithe', 'maitheyu@gmail.com', 'mik123', 'USER')
#buscar_usuario("maithe")
listar_usuarios()
