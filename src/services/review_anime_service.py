from src.config.bd_config import Anime, User, ReviewAnime, get_session 
from sqlalchemy.exc import IntegrityError

class ReviewAnimeCRUD():
    
    def __init__(self):
        pass

    def insert_review_anime(self, userID, animeID, nota_r, desc = None):
        review = ReviewAnime(user_id=userID, anime_id=animeID, nota=nota_r, descricao=desc)

        try:
            with get_session() as db:
                user = db.query(User).filter(User.id == userID).one_or_none()
                anime = db.query(Anime).filter(Anime.id == animeID).one_or_none()
                if user is None: return print("Usuário não encontrado.")
                if anime is None: return print("Anime não encontrado.")
                if nota_r is None: return print("Nota não informada.")

                db.add(review)
                db.commit()
                print(f"Review do usuário {user.nickname} do anime {anime.nome} inserida com sucesso!")
        except IntegrityError as e:
            db.rollback()
            return print(f"Erro capturado: {e}")
        except Exception as e:
            db.rollback()
            return print(f"Erro capturado: {e}")
        
    def delete_review_anime(self, reviewID):
        with get_session() as db:
            review = db.query(ReviewAnime).filter(ReviewAnime.id == reviewID).one_or_none()
            if review is None: return print("Review não encontrada")
            db.delete(review)
            return print("Review deletada com sucesso.")
        
    def listar_reviews_animes(self):
        with get_session() as db:
            return(
                db.query(ReviewAnime).order_by(ReviewAnime.nota.desc()).all()
            )
        
    def atualizar_review(self, reviewID, nova_nota : int = None, nova_desc : str = None):
        with get_session() as db:
            review = db.query(ReviewAnime).filter(ReviewAnime.id == reviewID).one_or_none()
            if review is None: return print("Review não encontrada")
            if nova_nota: review.nota = nova_nota
            if nova_desc: review.descricao = nova_desc 
            return print("Review atualizada com sucesso!")
        
    def buscar_Review(self, reviewID):
        with get_session() as db:
            review = db.query(ReviewAnime).filter(ReviewAnime.id == reviewID).one_or_none()
            if review is None: return print("Review não encontrada")
            return review



review = ReviewAnimeCRUD()
#review.insert_review_anime("e935e81f-f6b0-49d2-9919-5ee3b7915f5d", "356c0f51-39c7-43db-8c07-4bd55711535d", 5, "Gostei muito do anime, muito perfeito, melhor anime já feito!")      
#review.atualizar_review("7aeef9b9-efc2-41e2-b7ee-7d83f1c3dbe6", 4, "Passei a gostar menos depois de ilha dos tritoes, mas muito bom")
review.delete_review_anime("7aeef9b9-efc2-41e2-b7ee-7d83f1c3dbe6")  