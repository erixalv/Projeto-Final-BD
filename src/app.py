from flask import Flask, render_template, request, redirect, url_for, flash
from config.bd_config import User, get_session  # Importando User e get_session
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_KEY")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Configuração do banco de dados
USER = os.getenv("PG_USER")
PASSWORD = os.getenv("PG_PASSWORD")
BD_NAME = os.getenv("PG_BD_NAME")
PORT = os.getenv("PG_PORT")
HOST = os.getenv("PG_HOST")

def verificar_senha(user, senha_plana):
    return pwd_context.verify(senha_plana, user.senha_hash)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        # A sessão deve estar ativa para carregar o usuário
        with get_session() as db:  # Usando o gerenciador de contexto da sessão
            # Consultando o banco de dados para validar o usuário
            user = db.query(User).filter_by(email=email).first()

            if user and verificar_senha(user, senha):  # Chamada da função de verificação de senha
                return redirect(url_for('dashboard'))
            else:
                flash("Email ou senha incorretos!", 'danger')
                return render_template('index.html')
    
    return render_template('index.html')



@app.route('/home')
def dashboard():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
