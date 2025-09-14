from flask import Flask, render_template, request, redirect, url_for, flash
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from services.user_service import User_CRUD
from config.bd_config import User, get_session  # Importando User e get_session

user_managing = User_CRUD()

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

        with get_session() as db:
            # Busca o usuário dentro da sessão
            user = db.query(User).filter(User.email == email).one_or_none()

            if user is None:
                flash("Email ou senha incorretos!", 'danger')
                return render_template('index.html')

            # A verificação da senha já pode ser feita fora da sessão
            if pwd_context.verify(senha, user.senha_hash):
                if user.role == 'USER':
                    return redirect(url_for('cadastro_reviews'))
                else:
                    return redirect(url_for("cadastro_animes"))
            else:
                flash("Email ou senha incorretos!", 'danger')
                return render_template('index.html')

    return render_template('index.html')

@app.route('/user', methods=['GET', 'POST'])
def cadastro_reviews():
    return render_template('reviews.html')

@app.route('/admin', methods=['GET', 'POST'])
def cadastro_animes():
    return render_template('gerenciador.html')

if __name__ == '__main__':
    app.run(debug=True)
