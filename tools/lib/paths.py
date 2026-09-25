"""Где что лежит. Все скрипты берут пути отсюда, а не собирают их сами.

    site/       исходники страниц: HTML, стили, скрипты, картинки, шрифты
    content/    данные сайта в JSON, из них сборка пишет assets/js/*.js
    dist/       собранный сайт, его и выкладываем (в git не уходит)
    data/       исходники владельца: книга, анкета, фото, выгрузки (в git не уходят)
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
DIST = ROOT / "dist"
CONTENT = ROOT / "content"

# данные сайта: из них собираются assets/js/data.js, abstracts.js, citations.js, en-content.js
SITE_INFO = CONTENT / "site.json"
PEOPLE = CONTENT / "people.json"
DIRECTIONS = CONTENT / "directions.json"
PUBLICATIONS = CONTENT / "publications.json"
NEWS = CONTENT / "news.json"
ABSTRACTS = CONTENT / "abstracts.json"
CITATIONS = CONTENT / "citations.json"
ENGLISH = CONTENT / "english.json"

# ручные правки владельца: переживают любую пересборку
MANUAL = CONTENT / "manual"
MANUAL_ABSTRACTS = MANUAL / "abstracts.json"
MANUAL_DATES = MANUAL / "dates.json"
MANUAL_TAGS = MANUAL / "tags.json"
MANUAL_LINKS = MANUAL / "links.json"
MANUAL_NEWS_TITLES = MANUAL / "news_titles.json"

# собранное из внешних сервисов: заново собирать долго, поэтому лежит в git
COLLECTED = CONTENT / "collected"
PUBLICATIONS_DB = COLLECTED / "publications_db.json"
QUARTILES = COLLECTED / "journal_quartiles.json"

# рабочие листы: владелец правит их руками, скрипты забирают правки ключом --import
EDIT = CONTENT / "edit"

# исходники владельца, лежат только на его машине
DATA = ROOT / "data"
BOOK = DATA / "book" / "ЦМТ Мост.xlsx"
FORM = DATA / "news" / "011_Новости.docx"
PHOTOS = DATA / "photos"
SJR = DATA / "sjr"
FIGMA = DATA / "figma"

IMG = SITE / "assets" / "img"
