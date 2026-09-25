"""Собирает библиографические данные публикаций из Crossref по DOI в content/citations.json.

Из них сайт строит цитаты ГОСТ / MLA / APA и файлы BibTeX / EndNote / RefMan / RefWorks.
Запускать после добавления публикации: python tools/publications/citations.py
Уже скачанные DOI не перезапрашиваются (флаг --all обновляет все).
Работа без записи в Crossref получит цитату, собранную сайтом из своих полей.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib.paths import CITATIONS, PUBLICATIONS
from lib.store import load, rel, save
from lib.web import crossref


def clean(s):
    # в Crossref дефисы бывают типографскими (U+2010/2011), в цитатах нужен обычный
    return re.sub(r"[‐‑]", "-", s or "").strip()


def fetch(doi):
    m = crossref(doi, timeout=30)
    if not m:
        return None
    date = (m.get("published-print") or m.get("published-online") or m.get("issued") or {}).get("date-parts", [[None]])[0]
    return {
        "type": m.get("type"),
        "authors": [[clean(a.get("family")), clean(a.get("given"))] for a in m.get("author", [])],
        "title": clean((m.get("title") or [""])[0]),
        "container": clean((m.get("container-title") or [""])[0]),
        "volume": m.get("volume"),
        "issue": m.get("issue"),
        "page": clean(m.get("page") or m.get("article-number")),
        "year": date[0] if date else None,
        "publisher": clean(m.get("publisher")),
    }


def main():
    dois = [p["doi"].removeprefix("https://doi.org/") for p in load(PUBLICATIONS) if p.get("doi")]
    known = {} if "--all" in sys.argv else load(CITATIONS, {})
    result = {}
    for doi in dois:
        if doi in known:
            result[doi] = known[doi]
            continue
        got = fetch(doi)
        if got:
            result[doi] = got
            print("скачано", doi)
        else:
            print("нет данных", doi)
    save(CITATIONS, result)
    print(f"записано: {rel(CITATIONS)}, публикаций: {len(result)} из {len(dois)}")


if __name__ == "__main__":
    main()
