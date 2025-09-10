from sqlalchemy import (
    create_engine, Column, String, Integer, ForeignKey,
    CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import uuid
from passlib.context import CryptContext
from sqlalchemy.dialects.postgresql import UUID
from dotenv import load_dotenv
import os
from contextlib import contextmanager


load_dotenv()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

USER = os.getenv("PG_USER")
PASSWORD = os.getenv("PG_PASSWORD")
BD_NAME = os.getenv("PG_BD_NAME")
PORT = os.getenv("PG_PORT")
HOST = os.getenv("PG_HOST")

engine = create_engine(f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{BD_NAME}")
Base = declarative_base()

class User(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False)
    nickname = Column(String(15), nullable=False, unique=True)
    email = Column(String(254), nullable=False, unique=True)
    senha_hash = Column(String(200), nullable=False)
    role = Column(String(10), nullable=False)

    reviews_anime = relationship(
        "ReviewAnime", back_populates="user", cascade="all, delete-orphan"
    )
    reviews_episodio = relationship(
        "ReviewEpisode", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def senha(self):
        raise AttributeError("Senha não é legível. Use verificar_senha")

    @senha.setter
    def senha(self, senha_plana: str):
        self.senha_hash = pwd_context.hash(senha_plana)

    def verificar_senha(self, senha_plana: str) -> bool:
        return pwd_context.verify(senha_plana, self.senha_hash)


class Anime(Base):
    __tablename__ = "anime"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False, unique=True)
    genero = Column(String(20), nullable=False)
    studio = Column(String(30), nullable=False)
    numero_episodios = Column(Integer, nullable=False)
    sinopse = Column(String(100), nullable=False)

    __table_args__ = (
        CheckConstraint("numero_episodios >= 0", name="chk_anime_num_eps_nonneg"),
    )

    episodios = relationship(
        "Episodes", back_populates="anime", cascade="all, delete-orphan"
    )
    reviews_anime = relationship(
        "ReviewAnime", back_populates="anime", cascade="all, delete-orphan"
    )
    reviews_episodio = relationship(
        "ReviewEpisode", back_populates="anime", cascade="all, delete-orphan"
    )


class Episodes(Base):
    __tablename__ = "episodios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(70), nullable=False)
    anime_id = Column(UUID(as_uuid=True),
                      ForeignKey("anime.id", ondelete="CASCADE"),
                      nullable=False)
    sinopse = Column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint("anime_id", "nome", name="uq_episode_anime_nome"),
    )

    anime = relationship("Anime", back_populates="episodios")
    reviews = relationship(
        "ReviewEpisode", back_populates="episodio", cascade="all, delete-orphan"
    )


class ReviewAnime(Base):
    __tablename__ = "reviews_anime"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True),
                     ForeignKey("usuarios.id", ondelete="CASCADE"),
                     nullable=False)
    anime_id = Column(UUID(as_uuid=True),
                      ForeignKey("anime.id", ondelete="CASCADE"),
                      nullable=False)
    nota = Column(Integer, nullable=False)
    descricao = Column(String(140))

    __table_args__ = (
        CheckConstraint("nota >= 0 AND nota <= 5", name="chk_review_anime_nota_range"),
        UniqueConstraint("user_id", "anime_id", name="uq_review_anime_user_anime"),
    )

    user = relationship("User", back_populates="reviews_anime", passive_deletes=True)
    anime = relationship("Anime", back_populates="reviews_anime", passive_deletes=True)


class ReviewEpisode(Base):
    __tablename__ = "reviews_episodios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    episodio_id = Column(UUID(as_uuid=True), ForeignKey("episodios.id", ondelete="CASCADE"), nullable=False)
    anime_id = Column(UUID(as_uuid=True), ForeignKey("anime.id", ondelete="CASCADE"), nullable=False)
    nota = Column(Integer, nullable=False)
    descricao = Column(String(140))

    __table_args__ = (
        CheckConstraint("nota >= 0 AND nota <= 5", name="check_nota_range"),
        UniqueConstraint("user_id", "episodio_id",
        name="uq_review_episode_user_episodio"),
    )

    user = relationship("User", back_populates="reviews_episodio", passive_deletes=True)
    episodio = relationship("Episodes", back_populates="reviews", passive_deletes=True)
    anime = relationship("Anime", back_populates="reviews_episodio", passive_deletes=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base.metadata.create_all(engine)

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()