from bd_config import User, get_session  # Certifique-se de importar corretamente
from passlib.context import CryptContext

# Função para inserir um novo usuário
def inserir_usuario(nome, nickname, email, senha_plana):
    # Criação de um novo usuário
    user = User(
        nome=nome,
        nickname=nickname,
        email=email,
        senha=senha_plana  # Aqui a senha será automaticamente hashada pelo setter da classe User
    )

    # Inserir no banco de dados
    with get_session() as db:
        db.add(user)  # Adiciona o usuário à sessão
        db.commit()   # Confirma a transação (salva no banco)
        print("Usuário inserido com sucesso!")

# Exemplo de uso
inserir_usuario('João Silva', 'joao123', 'joao@example.com', 'senha_secreta')
