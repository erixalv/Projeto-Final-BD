from sqlalchemy import select, desc, func
from src.config.bd_config import (
    get_session, User, Anime, ReviewAnime, ReviewEpisode, Episodes
)

def contar_relacoes_unicas(chaveDoObjeto):
    with get_session() as session:
        query = select(func.count(chaveDoObjeto))
        total = session.execute(query).scalar_one()
        return total
    
def media_notas_por_anime():
    with get_session() as session:
        query = select(
            Anime.nome,
            func.count(ReviewAnime.anime_id),
            func.avg(ReviewAnime.nota)
        ).join(ReviewAnime, ReviewAnime.anime_id == Anime.id, isouter=False).group_by(Anime.id, Anime.nome).order_by(desc(func.count(ReviewAnime.nota)))
        return session.execute(query).all()
    
def media_notas_por_episodio():
    with get_session() as session:
        query = select(
            Anime.nome,
            func.count(ReviewEpisode.anime_id),
            func.avg(ReviewEpisode.nota)
        ).join(ReviewEpisode, ReviewEpisode.anime_id == Anime.id, isouter=False).group_by(Anime.id, Anime.nome).order_by(desc(func.count(ReviewEpisode.nota)))
        return session.execute(query).all()
    
def contar_usuarios_avaliadores():
    with get_session() as session:
        query = select(
            func.count(func.distinct(ReviewAnime.user_id))
        )
        qtd = session.execute(query).scalar_one()
        return qtd

    
print(contar_usuarios_avaliadores())