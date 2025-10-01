from sqlalchemy import select, desc, func, text
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
    
def anime_mais_bem_avaliado():
    """Retorna o anime com a maior média de notas."""
    with get_session() as db:
        query = text("""
            SELECT nome, avg
            FROM vw_media_nota_episodio
            ORDER BY avg DESC
            LIMIT 1;
        """)
        result = db.execute(query).first()
        return {"nome": result[0], "media": float(result[1])} if result else None

def anime_com_mais_reviews():
    """Retorna o anime com o maior número de reviews."""
    with get_session() as db:
        query = text("""
            SELECT nome, count
            FROM vw_media_nota_episodio
            ORDER BY count DESC
            LIMIT 1;
        """)
        result = db.execute(query).first()
        return {"nome": result[0], "reviews": int(result[1])} if result else None

def total_usuarios_cadastrados():
    """Retorna o número total de usuários cadastrados."""
    with get_session() as db:
        query = text("SELECT COUNT(id) FROM usuarios;")
        count = db.execute(query).scalar_one()
        return count

    
print(contar_usuarios_avaliadores())