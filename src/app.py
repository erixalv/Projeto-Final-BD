from flask import Flask, render_template, request, redirect, url_for, flash, session
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from services.user_service import User_CRUD
from services.anime_service import Anime_CRUD
from services.episode_service import Episode_CRUD
from services.review_anime_service import ReviewAnimeCRUD
from services.review_episode_service import ReviewEpisodeCRUD
from services.report import media_notas_por_anime
from config.bd_config import User, Anime, Episodes, get_session
from services.report import media_notas_por_anime, anime_mais_bem_avaliado, anime_com_mais_reviews, total_usuarios_cadastrados


from sqlalchemy import text

user_managing = User_CRUD()

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_KEY")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

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
            user = db.query(User).filter(User.email == email).one_or_none()

            if user is None:
                flash("Email ou senha incorretos!", 'danger')
                return render_template('index.html')

            if pwd_context.verify(senha, user.senha_hash):
                session['usuario_id'] = user.id
                if user.role == 'USER':
                    return redirect(url_for('cadastro_reviews'))
                else:
                    return redirect(url_for("gerenciador_animes"))
            else:
                flash("Email ou senha incorretos!", 'danger')
                return render_template('index.html')

    return render_template('index.html')

@app.route('/relatorios', methods=['GET'])
def relatorios():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        flash("Você precisa estar logado!", "danger")
        return redirect(url_for('login'))

    with get_session() as db:
        # Consulta que você já tinha (Média de notas por episódio)
        media_anime_rows = db.execute(
            text("SELECT nome, count, avg FROM vw_media_nota_episodio")
        ).mappings().all()

        # Consulta que você já tinha (Contagem de usuários avaliadores)
        qtd_usuarios_avaliadores = db.execute(
            text("SELECT fn_contar_usuarios_avaliadores() AS qtd")
        ).scalar_one()

        # Consulta que você já tinha (Média de notas por anime)
        rows = media_notas_por_anime()
        media_por_anime = [
            {
                "anime_nome": r[0],
                "qtde_reviews": int(r[1]) if r[1] is not None else 0,
                "media_nota": float(r[2]) if r[2] is not None else 0.0
            }
            for r in rows
        ]


    total_de_usuarios = total_usuarios_cadastrados()
    anime_top_avaliado = anime_mais_bem_avaliado()
    anime_top_reviews = anime_com_mais_reviews()

    return render_template(
        'relatorios.html',
        media_anime=media_anime_rows,
        qtd_usuarios=qtd_usuarios_avaliadores,
        media_por_anime=media_por_anime,
        total_de_usuarios=total_de_usuarios,
        anime_top_avaliado=anime_top_avaliado,
        anime_top_reviews=anime_top_reviews
    )

@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        flash("Você precisa estar logado!", "danger")
        return redirect(url_for('login'))

    usuario_busca = None
    usuarios_lista = None

    if request.method == 'POST':
        acao = request.form.get('acao')

        # ---------- CADASTRAR ----------
        if acao == 'cadastrarUsuario':
            nome = request.form.get('nome')
            nickname = request.form.get('nickname')
            email = request.form.get('email')
            senha = request.form.get('senha')
            role = request.form.get('role', 'USER')

            try:
                msg = user_managing.inserir_usuario(nome, nickname, email, senha, role)
                flash("Usuário inserido com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao inserir usuário: {e}", "danger")

        # ---------- REMOVER ----------
        elif acao == 'removerUsuario':
            nickname = request.form.get('nickname_r')
            try:
                msg = user_managing.remover_usuario(nickname)
                flash(msg or "Usuário removido.", "success")
            except Exception as e:
                flash(f"Erro ao remover: {e}", "danger")

        # ---------- BUSCAR POR NICK ----------
        elif acao == 'buscarUsuarioPorNick':
            nickname = request.form.get('nickname_l')
            usuario_busca = user_managing.buscar_usuario_por_nick(nickname)
            if not usuario_busca:
                flash("Usuário não encontrado.", "warning")

        # ---------- BUSCAR POR EMAIL ----------
        elif acao == 'buscarUsuarioPorEmail':
            email = request.form.get('email_l')
            usuario_busca = user_managing.buscar_usuario_por_email(email)
            if not usuario_busca:
                flash("Usuário não encontrado.", "warning")

        # ---------- LISTAR TODOS ----------
        elif acao == 'listarUsuarios':
            usuarios_lista = user_managing.listar_usuarios()

        # ---------- ATUALIZAR SENHA ----------
        elif acao == 'atualizarSenha':
            nickname = request.form.get('nickname_senha')
            senha_atual = request.form.get('senha_atual')
            senha_nova = request.form.get('senha_nova')
            try:
                user_managing.atualizar_senha(nickname, senha_atual, senha_nova)
                flash("Senha atualizada (se os dados estiverem corretos).", "info")
            except Exception as e:
                flash(f"Erro ao atualizar senha: {e}", "danger")

        # ---------- ATUALIZAR DADOS ----------
        elif acao == 'atualizarDados':
            nickname = request.form.get('nickname_dados')
            nome_novo = request.form.get('nome_novo') or None
            email_novo = request.form.get('email_novo') or None
            try:
                msg = user_managing.atualizar_dados(nickname, nome_novo, email_novo)
                flash("Dados atualizados (se os dados estiverem corretos).", "info")
            except Exception as e:
                flash(f"Erro ao atualizar dados: {e}", "danger")

    return render_template(
        'usuarios.html',
        usuario=usuario_busca,
        usuarios=usuarios_lista
    )


@app.route('/user', methods=['GET', 'POST'])
def cadastro_reviews():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        flash("Você precisa estar logado!", "danger")
        return redirect(url_for('login'))

    anime_review = ReviewAnimeCRUD()
    episode_review = ReviewEpisodeCRUD()

    resultado_busca_anime = None
    resultado_busca_ep = None
    reviews_animes = []
    reviews_episodios = []

    if request.method == "POST":
        acao = request.form.get("acao")

        # -------------------- ANIMES --------------------
        if acao == "inserirReviewAnime":
            nome_anime = request.form['nome_anime']
            nota = int(request.form['nota'])
            comentario = request.form['comentario']

            with get_session() as db:
                anime = db.query(Anime).filter(Anime.nome == nome_anime).first()
                if anime:
                    anime_review.insert_review_anime(usuario_id, anime.id, nota, comentario)
                    flash("Review de anime inserida com sucesso!", "success")
                else:
                    flash("Anime não encontrado!", "danger")

        elif acao == "removerReviewAnime":
            review_id = request.form['review_id']
            anime_review.delete_review_anime(review_id)
            flash("Review de anime removida!", "success")

        elif acao == "atualizarReviewAnime":
            review_id = request.form['review_id']
            nova_nota = request.form.get('nova_nota', None)
            novo_comentario = request.form.get('novo_comentario', None)

            nova_nota = int(nova_nota) if nova_nota else None
            anime_review.atualizar_review(review_id, nova_nota, novo_comentario)
            flash("Review de anime atualizada!", "success")

        elif acao == "buscarReviewAnime":
            review_id = request.form['review_id']
            resultado = anime_review.buscar_Review(review_id)
            if resultado:
                resultado_busca_anime = resultado
            else:
                resultado_busca_anime = {"erro": "Review não encontrada."}

        elif acao == "listarReviewsAnimes":
            reviews_animes = anime_review.listar_reviews_usuario(usuario_id)

        # -------------------- EPISÓDIOS --------------------
        elif acao == "inserirReviewEpisodio":
            nome_anime = request.form['nome_anime']
            numero_ep = int(request.form['numero_ep'])
            nota = int(request.form['nota'])
            comentario = request.form['comentario']

            with get_session() as db:
                anime = db.query(Anime).filter(Anime.nome == nome_anime).first()
                episodio = db.query(Episodes).filter(Episodes.num_ep == numero_ep, Episodes.anime_id == anime.id).first()
                
                if anime and episodio:
                    episode_review.insert_review_episode(usuario_id, episodio.id, anime.id, nota, comentario)
                    flash("Review de episódio inserida com sucesso!", "success")
                else:
                    flash("Anime ou episódio não encontrado!", "danger")

        elif acao == "removerReviewEpisodio":
            review_id = request.form['review_id']
            episode_review.delete_review_episode(review_id)
            flash("Review de episódio removida!", "success")

        elif acao == "atualizarReviewEpisodio":
            review_id = request.form['review_id']
            nova_nota = request.form.get('nova_nota', None)
            novo_comentario = request.form.get('novo_comentario', None)

            nova_nota = int(nova_nota) if nova_nota else None
            episode_review.atualizar_review(review_id, nova_nota, novo_comentario)
            flash("Review de episódio atualizada!", "success")

        elif acao == "buscarReviewEpisodio":
            review_id = request.form['review_id']
            resultado = episode_review.buscar_Review(review_id)
            if resultado:
                resultado_busca_ep = resultado
            else:
                resultado_busca_ep = {"erro": "Review não encontrada."}

        elif acao == "listarReviewsEpisodios":
            reviews_episodios = episode_review.listar_reviews_usuario(usuario_id)

    return render_template(
        "reviews.html",
        resultado_busca_anime=resultado_busca_anime,
        resultado_busca_ep=resultado_busca_ep,
        reviews_animes=reviews_animes,
        reviews_episodios=reviews_episodios,
    )


@app.route('/admin', methods=['GET', 'POST'])
def gerenciador_animes():
    anime = Anime_CRUD()
    anime_dict = None
    anime_edit = None
    lista_nomes = None

    episodio = Episode_CRUD()
    ep_dict = None
    episodios_agrupados = {}
    ep_edit = None

    if request.method == 'POST':
        acao = request.form.get('acao')


        #CRUD DE ANIMES
        #-----------------------------------------------------------
        if acao =='cadastrarAnime':
            nome = request.form['nome_do_anime']
            genero = request.form['genero_do_anime']
            estudio = request.form['estudio_do_anime']
            numero_de_eps = request.form['numero_de_ep']
            sinopse = request.form['sinopse_do_anime']

            with get_session() as db:
                anime.inserir_anime(nome, genero, estudio, numero_de_eps, sinopse)
            flash('Anime inserido!', 'sucess')
        
        if acao == 'removerAnime':
            nome = request.form['nome_do_anime_r']
            with get_session() as db:
                inst = anime.buscar_anime_por_nome(nome, db=db)
                if inst: 
                    anime.remover_instancia(inst=inst, db=db)
                    flash('Anime removido!', 'success')
                else:
                    flash('Erro', 'error')
        
        if acao == 'listarAnime':
            nome = request.form['nome_do_anime_l']
            with get_session() as db:
                anime_b = anime.buscar_anime_por_nome(nome, db=db)
                if not anime_b:
                    flash('Anime não enontrado.', 'warning')
                else:
                    anime_dict = {
                        'id' : anime_b.id,
                        'nome' : anime_b.nome,
                        'genero' : anime_b.genero,
                        'estudio' : anime_b.studio,
                        'numero_de_eps' : anime_b.numero_episodios,
                        'sinopse' : anime_b.sinopse
                    }
        
        if acao == 'listarAllAnime':
            with get_session() as db:
                lista_nomes = anime.listar_nomes_animes(db=db)

        if acao == 'prepararAlteracao':
            nome = request.form['nome_do_anime_edit']
            with get_session() as db:
                anime_b = anime.buscar_anime_por_nome(nome, db=db)
                if not anime_b:
                    flash('Anime não encontrado.', 'warning')
                else:
                    anime_dict = {
                        'id': anime_b.id,
                        'nome': anime_b.nome,
                        'genero': anime_b.genero,
                        'estudio': anime_b.studio,            
                        'numero_de_eps': anime_b.numero_episodios,
                        'sinopse': anime_b.sinopse
                    }
                    anime_edit = {
                        'id': anime_b.id,
                        'nome': anime_b.nome,
                        'genero': anime_b.genero,
                        'studio': anime_b.studio,
                        'numero_episodios': anime_b.numero_episodios,
                        'sinopse': anime_b.sinopse
                    }
                    return render_template('gerenciador.html', anime=anime_dict, lista_nomes=lista_nomes, anime_edit=anime_edit)

        if acao == 'alterarAnime':
            anime_id = request.form['anime_id']
            nome = request.form.get('nome_edit', None)
            genero = request.form.get('genero_edit', None)
            studio = request.form.get('studio_edit', None)
            numero_raw = request.form.get('numero_edit', None)
            sinopse = request.form.get('sinopse_edit', None)

            numero_episodios = None
            if numero_raw not in (None, ''):
                try:
                    numero_episodios = int(numero_raw)
                except ValueError:
                    flash('Número de episódios inválido.', 'danger')
                    return render_template('gerenciador.html', anime=anime_dict, lista_nomes=lista_nomes)

            try:
                atualizado = anime.atualizar_anime(
                    anime_id=anime_id,
                    nome=nome,
                    genero=genero,
                    studio=studio,
                    numero_episodios=numero_episodios,
                    sinopse=sinopse
                )
                if atualizado:
                    flash(f"Anime '{atualizado.nome}' atualizado com sucesso!", 'success')
                else:
                    flash('Anime não encontrado para atualização.', 'warning')
            except Exception as e:
                flash(f'Erro ao atualizar: {e}', 'danger')
        #-----------------------------------------------------------


        #CRUD DE EPISODIOS
        #-----------------------------------------------------------
        if acao =='cadastrarEpisodio':
            nome = request.form['nome_do_episodio']
            num_ep = request.form['numero_do_ep']
            animeNome = request.form['anime_do_ep']
            sinopse = request.form['sinopse_do_episodio']

            with get_session() as db:
                anime_obj = anime.buscar_anime_por_nome(animeNome, db)
                episodio.inserir_episodio(num_ep=num_ep, nome=nome, anime_id=anime_obj.id, sinopse=sinopse)
            flash('Episódio inserido!', 'success')

        if acao == 'removerEpisodio':
            nome = request.form['nome_do_episodio_r']
            with get_session() as db:
                ep = episodio.buscar_episodio_por_nome(nome, db=db)
                if ep: 
                    episodio.remover_episodio(ep.id)
                    flash('Episódio removido!', 'success')
                else:
                    flash('Erro', 'error')

        if acao == 'listarEpisodio':
            nome = request.form['nome_do_episodio_l']
            with get_session() as db:
                ep_b = episodio.buscar_episodio_por_nome(nome, db=db)
                if not ep_b:
                    flash('Episódio não encontrado.', 'warning')
                else:
                    ep_dict = {
                        'id' : ep_b.id,
                        'nome' : ep_b.nome,
                        'numero_ep' : ep_b.num_ep,
                        'anime_id' : ep_b.anime_id,
                        'sinopse' : ep_b.sinopse
                    }
                 
        if acao == 'listarAllEps':
            with get_session() as db:
                # 1. Chame a nova função que busca os dados ordenados
                resultados_db = episodio.listar_episodios_por_anime(db)

                # 2. Processe os resultados para agrupar em um dicionário
                episodios_agrupados = {}
                for item in resultados_db:
                    # Se o nome do anime ainda não for uma chave no dicionário...
                    if item.anime_nome not in episodios_agrupados:
                        # ...crie a chave com uma lista vazia.
                        episodios_agrupados[item.anime_nome] = []
                    
                    # Adicione o episódio (como um dicionário) à lista daquele anime.
                    episodios_agrupados[item.anime_nome].append({
                        "num_ep": item.num_ep,
                        "nome": item.episodio_nome
                    })

        if acao == 'prepararAlteracaoEp':
            nome = request.form['nome_do_episodio_edit']
            with get_session() as db:
                ep_b = episodio.buscar_episodio_por_nome(nome, db=db)
                if not ep_b:
                    flash('Episódio não encontrado.', 'warning')
                else:
                    ep_dict = {
                        'id': ep_b.id,
                        'nome': ep_b.nome,
                        'numero_ep': ep_b.num_ep,
                        'anime_id': ep_b.anime_id,
                        'sinopse': ep_b.sinopse
                    }
                    ep_edit = {
                        'id': ep_b.id,
                        'nome': ep_b.nome,
                        'num_ep': ep_b.num_ep,
                        'sinopse': ep_b.sinopse
                    }
                    return render_template(
                        'gerenciador.html',
                        anime=anime_dict,
                        lista_nomes=lista_nomes,
                        anime_edit=anime_edit,
                        ep=ep_dict,
                        lista_nomes_eps=episodios_agrupados,
                        ep_edit=ep_edit
                    )

        if acao == 'alterarEpisodio':
            episodio_id = request.form.get('episodio_id')
            nome = request.form.get('nome_edit_ep', None)
            numero_raw = request.form.get('numero_edit_ep', None)
            sinopse = request.form.get('sinopse_edit_ep', None)

            num_ep = None
            if numero_raw not in (None, ''):
                try:
                    num_ep = int(numero_raw)
                except ValueError:
                    flash('Número do episódio inválido.', 'danger')
                    return render_template(
                        'gerenciador.html',
                        anime=anime_dict,
                        lista_nomes=lista_nomes,
                        anime_edit=anime_edit,
                        ep=ep_dict,
                        lista_nomes_eps=episodios_agrupados,
                        ep_edit=ep_edit
                    )

            try:
                with get_session() as db:
                    atualizado = episodio.atualizar_episodio(
                        episodio_id=episodio_id,
                        num_ep=num_ep,
                        nome=nome,
                        sinopse=sinopse,
                        db=db
                    )
                    if atualizado:
                        flash(f"Episódio '{atualizado.nome}' atualizado com sucesso!", 'success')
                    else:
                        flash('Episódio não encontrado para atualização.', 'warning')
            except Exception as e:
                flash(f'Erro ao atualizar episódio: {e}', 'danger')
        #-----------------------------------------------------------


    return render_template('gerenciador.html', anime=anime_dict, lista_nomes=lista_nomes, anime_edit=anime_edit, ep=ep_dict, episodios_agrupados = episodios_agrupados, ep_edit=ep_edit)

if __name__ == '__main__':
    app.run(debug=True)
