from src.config.bd_config import Episodes, Anime, get_session
from sqlalchemy.exc import IntegrityError

class Episode_CRUD:

    def init(self):
        pass

    def inserir_episodio(self, num_ep, nome, anime_id, sinopse):
        episodio = Episodes(
            nome=nome,
            num_ep=num_ep,
            anime_id=anime_id,
            sinopse=sinopse
        )
        try:
            with get_session() as db:
                anime = db.query(Anime).filter(Anime.id == anime_id).one_or_none()
                if anime is None:
                    print("Anime não encontrado para associar ao episódio.")
                    return None

                db.add(episodio)
                db.commit()
                print(f"Episódio '{nome}' do anime '{anime.nome}' inserido com sucesso!")
                return episodio
        except IntegrityError as e:
            db.rollback()
            print(f"Erro de integridade: {e.orig}")
            return None
        except Exception as e:
            db.rollback()
            print(f"Erro inesperado: {e}")
            return None

    def listar_episodios(self):
        with get_session() as db:
            return db.query(Episodes).order_by(Episodes.nome.asc()).all()

    def buscar_episodio(self, episodio_id):
        with get_session() as db:
            ep = db.query(Episodes).filter(Episodes.id == episodio_id).one_or_none()
            if ep is None:
                print("Episódio não encontrado.")
                return None
            return ep

    def listar_por_anime(self, anime_id):
        with get_session() as db:
            return db.query(Episodes).filter(Episodes.anime_id == anime_id).all()

    def atualizar_episodio(self, episodio_id, num_ep = None, nome=None, sinopse=None):
        with get_session() as db:
            ep = db.query(Episodes).filter(Episodes.id == episodio_id).one_or_none()
            if ep is None:
                print("Episódio não encontrado.")
                return None

            if nome is not None:
                ep.nome = nome
            if sinopse is not None:
                ep.sinopse = sinopse
            if num_ep is not None:
                ep.num_ep = num_ep

            db.commit()
            print(f"Episódio '{ep.nome}' atualizado com sucesso!")
            return ep

    def remover_episodio(self, episodio_id):
        with get_session() as db:
            ep = db.query(Episodes).filter(Episodes.id == episodio_id).one_or_none()
            if ep is None:
                print("Episódio não encontrado.")
                return None
            db.delete(ep)
            db.commit()
            print(f"Episódio '{ep.nome}' removido com sucesso.")
            return True


episode_service = Episode_CRUD()

#episode_service.inserir_episodio(24, "Thaumazein", "31ce4639-a1a3-4d1a-b409-9e5e271646ae", "Durante uma entrega, Albert encontra um padre misterioso que o incentiva a confessar seus pecados.")
episode_service.inserir_episodio(1046, "Luffy derrota Kaido", "356c0f51-39c7-43db-8c07-4bd55711535d", "Luffy vence Kaido.")
#episode_service.atualizar_episodio("111bbb0a-2760-4d1b-b073-d0d130476b7c", num_ep=1047)
#episode_service.remover_episodio("111bbb0a-2760-4d1b-b073-d0d130476b7c")