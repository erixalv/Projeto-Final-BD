from src.config.bd_config import Anime, get_session
from sqlalchemy.exc import IntegrityError

class Anime_CRUD:

    def init(self):
        pass

    def inserir_anime(self, nome, genero, studio, numero_episodios, sinopse):
        anime = Anime(
            nome=nome,
            genero=genero,
            studio=studio,
            numero_episodios=numero_episodios,
            sinopse=sinopse
        )
        try:
            with get_session() as db:
                db.add(anime)
                db.commit()
                print(f"Anime '{nome}' inserido com sucesso!")
                return anime
        except IntegrityError as e:
            db.rollback()
            print(f"Erro de integridade: {e.orig}")
            return None
        except Exception as e:
            db.rollback()
            print(f"Erro inesperado: {e}")
            return None

    def listar_animes(self):
        with get_session() as db:
            return db.query(Anime).order_by(Anime.nome.asc()).all()

    def buscar_anime(self, anime_id):
        with get_session() as db:
            anime = db.query(Anime).filter(Anime.id == anime_id).one_or_none()
            if anime is None:
                print("Anime não encontrado.")
                return None
            return anime

    def atualizar_anime(self, anime_id, nome=None, genero=None, studio=None, numero_episodios=None, sinopse=None):
        with get_session() as db:
            anime = db.query(Anime).filter(Anime.id == anime_id).one_or_none()
            if anime is None:
                print("Anime não encontrado.")
                return None

            if nome is not None:
                anime.nome = nome
            if genero is not None:
                anime.genero = genero
            if studio is not None:
                anime.studio = studio
            if numero_episodios is not None:
                anime.numero_episodios = numero_episodios
            if sinopse is not None:
                anime.sinopse = sinopse

            db.commit()
            print(f"Anime '{anime.nome}' atualizado com sucesso!")
            return anime

    def remover_anime(self, anime_id):
        with get_session() as db:
            anime = db.query(Anime).filter(Anime.id == anime_id).one_or_none()
            if anime is None:
                print("Anime não encontrado.")
                return None
            db.delete(anime)
            db.commit()
            print(f"Anime '{anime.nome}' removido com sucesso.")
            return True


anime_service = Anime_CRUD()

#anime_service.inserir_anime("Orbe: Sobre os Movimentos da Terra", "Histórico", "Madhouse", 28, "")

#print(anime_service.remover_anime("5b3a05eb-adf3-41a4-958a-83ec3d61799f"))

anime_service.atualizar_anime("31ce4639-a1a3-4d1a-b409-9e5e271646ae", numero_episodios=26)