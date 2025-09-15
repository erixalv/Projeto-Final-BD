from src.config.bd_config import Anime, User, Episodes, ReviewEpisode, get_session 
from sqlalchemy.exc import IntegrityError

class ReviewEpisodeCRUD():

    def __init__(self):
        pass

    def insert_review_episode(self, userID, episodeID, animeID, nota_r, desc = None):
        review = ReviewEpisode(user_id=userID, episodio_id=episodeID, anime_id=animeID, nota=nota_r, descricao=desc)

        try:
            with get_session() as db:
                user = db.query(User).filter(User.id == userID).one_or_none()
                anime = db.query(Anime).filter(Anime.id == animeID).one_or_none()
                episode = db.query(Episodes).filter(Episodes.id == episodeID).one_or_none()
                if user is None: return print("Usuário não encontrado.")
                if anime is None: return print("Anime não encontrado.")
                if episode is None: return print("Episódio não encontrado.")
                if nota_r is None: return print("Nota não informada.")

                db.add(review)
                db.commit()
                print(f"Review do usuário {user.nickname} do episódio {episode.nome} do anime {anime.nome} inserida com sucesso!")
        except IntegrityError as e:
            db.rollback()
            return print(f"Erro capturado: {e}")
        except Exception as e:
            db.rollback()
            return print(f"Erro capturado: {e}")
    
    def delete_review_episode(self, reviewID):
        with get_session() as db:
            review = db.query(ReviewEpisode).filter(ReviewEpisode.id == reviewID).one_or_none()
            if review is None: return print("Review não encontrada")
            db.delete(review)
            return print("Review deletada com sucesso.")
        
    def listar_reviews_episodios(self):
        with get_session() as db:
            rows = (
                db.query(ReviewEpisode.id, ReviewEpisode.user_id, ReviewEpisode.episodio_id, ReviewEpisode.anime_id, ReviewEpisode.nota, ReviewEpisode.descricao)
                .order_by(ReviewEpisode.nota.desc())
                .all()
            )
            return [dict(r._mapping) for r in rows]
        
    def atualizar_review(self, reviewID, nova_nota : int = None, nova_desc : str = None):
        with get_session() as db:
            review = db.query(ReviewEpisode).filter(ReviewEpisode.id == reviewID).one_or_none()
            if review is None: return print("Review não encontrada")
            if nova_nota: review.nota = nova_nota
            if nova_desc: review.descricao = nova_desc 
            return print("Review atualizada com sucesso!")
        
    def buscar_Review(self, reviewID):
        with get_session() as db:
            r = (
                db.query(ReviewEpisode.id, ReviewEpisode.user_id, ReviewEpisode.episodio_id, ReviewEpisode.anime_id, ReviewEpisode.nota, ReviewEpisode.descricao)
                .filter(ReviewEpisode.id == reviewID)
                .one_or_none()
            )
            if r is None:
                return None
            return dict(r._mapping)
        
review = ReviewEpisodeCRUD()

#review.insert_review_episode("e935e81f-f6b0-49d2-9919-5ee3b7915f5d", "b25793bf-b41c-4ea7-aafe-e14a9332a992","356c0f51-39c7-43db-8c07-4bd55711535d", 5, "Melhor ep!")  
#review.atualizar_review("f4f52ef6-493b-4178-87bb-935aadebe4c5", nova_desc="Amei muito o ep, o final então...")
#review.delete_review_anime("f4f52ef6-493b-4178-87bb-935aadebe4c5")