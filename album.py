import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func


DB_PATH = "sqlite:///albums.sqlite3"
Base = declarative_base()


class Album(Base):
    """
    Описывает структуру таблицы album для хранения записей музыкальной библиотеки
    """

    __tablename__ = "album"

    id = sa.Column(sa.INTEGER, primary_key=True, autoincrement=True)
    year = sa.Column(sa.INTEGER)
    artist = sa.Column(sa.TEXT)
    genre = sa.Column(sa.TEXT)
    album = sa.Column(sa.TEXT)


def connect_db():
    """
    Устанавливает соединение к базе данных, создает таблицы, если их еще нет и возвращает объект сессии 
    """
    engine = sa.create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)
    return session()

def get_all_artists():
    """
    Находит всех артистов
    """
    session = connect_db()
    artist = session.query(Album.artist).distinct().all()
    return sorted( [ art[0] for art in artist ] )

def find(artist):
    """
    Находит все альбомы в базе данных по заданному артисту
    """
    session = connect_db()
    albums = session.query(Album)\
             .filter( func.lower(Album.artist) == artist.lower() )\
             .all()
    return albums

def get_album_exactly(album_data):
    """
    Находит альбомы в базе данных по совпадению всех полей
    """
    session = connect_db()
    query = session.query(Album)
    for key, val in album_data.items():
       query = query.filter(getattr(Album, key) == val)
    return query.all()

def save(album_data):
    """
    Пишет данные нового альбома в базу
    """
    new_album = Album()
    for key, val in album_data.items():
       setattr(new_album, key, val)
    session = connect_db()
    session.add(new_album)
    session.commit()
