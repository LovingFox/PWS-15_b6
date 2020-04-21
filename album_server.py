from bottle import route
from bottle import run
from bottle import HTTPError
from bottle import request
from urllib.parse import quote

import album

from html_format import Tag, HTML, TopLevelTag

START="/"
ALBUMS="/albums"

@route(START)
def start():
    """
    Стартовая страница, выводит всех артистов, генерируя
    ссылки на запрос албомов каждого из них
    Так же выводит форму добавления нового альбома
    """
    # запрос всех артистов в базе
    artists = album.get_all_artists()

    with HTML(notprint=True) as doc:
       with TopLevelTag("head") as head:
          head += Tag("title", text = "База album")
          doc += head

       with TopLevelTag("body") as body:
          body += Tag("h1", text = "Работа с базой album")

          if artists:
             body += Tag("h3", text = "Найти все альбомы следующих артистов")

             # генерируем список артистов и ссылки на запрос их альбомов
             with Tag("ul") as ul:
                for artist in artists:
                   with Tag("li") as li:
                      li += Tag("a", href="{}/{}".format(ALBUMS, quote(artist)), text = artist)
                      ul += li
                body += ul
          else:
             body += Tag("h3", text = "Ни одного альбома в базе нет")


          # Форма для сохранения нового альбома
          body += Tag("h3", text = "Добавить новый альбом")
          with Tag("form", action=ALBUMS, method="post") as form:
             form += Tag("lable", _for="artist", text="Артист:") + Tag("br", is_single=True)
             form += Tag("input", type="text", id="artist", name="artist", is_single=True)
             form += Tag("br", is_single=True)
             form += Tag("lable", _for="album", text="Альбом:") + Tag("br", is_single=True)
             form += Tag("input", type="text", id="album", name="album", is_single=True)
             form += Tag("br", is_single=True)
             form += Tag("lable", _for="genre", text="Жанр:") + Tag("br", is_single=True)
             form += Tag("input", type="text", id="genre", name="genre", is_single=True)
             form += Tag("br", is_single=True)
             form += Tag("lable", _for="year", text="Год:") + Tag("br", is_single=True)
             form += Tag("input", type="text", id="year", name="year", is_single=True)
             form += Tag("br", is_single=True)
             form += Tag("button", type="submit", text="Добавить")
             body += form

          doc += body


       result = str(doc)

    return result

@route("{}/<artist>".format(ALBUMS))
def albums(artist):
    """
    Отобразить все альбомы артиста
    """
    albums_list = album.find(artist)
    if not albums_list:
        message = "Альбомов {} не найдено".format(artist)
        result = HTTPError(404, message)
    else:
        with HTML(notprint=True) as doc:
           with TopLevelTag("head") as head:
              head += Tag("title", text = "Найденные альбомы")
              doc += head

           with TopLevelTag("body") as body:
              body += Tag("a", href=START, text = "На стартовую страницу")

              body += Tag("h1", text = "Исполнитель {}".format(artist.title()))
              body += Tag("h2", text = "Количество альбомов: {}".format( len(albums_list) ))
              body += Tag("p", text = "Список альбомов:")

              with Tag("ul") as ul:
                 for alb in albums_list:
                    ul += Tag("li",
                              text = "{album} ({year}, {genre})"\
                              .format(album=alb.album, year=alb.year, genre=alb.genre) )
                 body += ul

              doc += body

           result = str(doc)

    return result

def validate_data(data):
   """
   Валидация данных перед тем, как записать их в базу
   """
   # проверяем, что все поля есть и они не пустые
   for k, v in data.items():
      if v is None or not v.strip():
         return "Пустой элемент {}".format(k)

   # проверяем, что year является числом
   try:
      data["year"] = int(data["year"])
   except ValueError:
      return "Год указан неверно"

def id_album_exists(data):
    """
    Возвращает ID альбома, если совпадение по всем полям
    """
    albums_list = album.get_album_exactly(data)
    if albums_list:
       return albums_list[0].id

@route(ALBUMS, method="POST")
def new_album():
    """
    Сохранение нового альбома методом POST
    """
    album_data = {
        "artist": request.forms.get("artist"),
        "album": request.forms.get("album"),
        "genre": request.forms.get("genre"),
        "year": request.forms.get("year"),
    }

    # проверяем все поля на корректность
    error = validate_data(album_data)
    if error:
        return HTTPError(400, error)

    # проверяем, есть ли в базе альбом с теми же данными
    alb_id = id_album_exists(album_data)
    if alb_id:
        return HTTPError(409, "Альбом уже есть, id: {}".format(alb_id))

    # все проверки пройдены, сохраняем новый альбом
    album.save(album_data)
    with HTML(notprint=True) as doc:
       with TopLevelTag("head") as head:
          head += Tag("title", text = "Сохранение альбома")
          doc += head

       with TopLevelTag("body") as body:
          body += Tag("a", href=START, text = "На стартовую страницу")
          body += Tag("h2", text = "Альбом сохранен")
          doc += body

    return str(doc)
    

if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True)
