"""Собирает библиографические данные публикаций из Crossref по DOI в assets/js/citations.js.

Из них сайт строит цитаты ГОСТ / MLA / APA и файлы BibTeX / EndNote / RefMan / RefWorks.
Запускать после добавления публикации в data.js: python tools/fetch_citations.py
Уже скачанные DOI не перезапрашиваются (флаг --all обновляет все).
"""
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "js" / "data.js"
OUT = ROOT / "assets" / "js" / "citations.js"
HEADER = "/* Сгенерировано tools/fetch_citations.py из Crossref, руками не править. */\nwindow.CITATIONS = "


def clean(s):
    # в Crossref дефисы бывают типографскими (U+2010/2011), в цитатах нужен обычный
    return re.sub(r"[‐‑]", "-", s or "").strip()


def fetch(doi):
    req = urllib.request.Request(
        f"https://api.crossref.org/works/{doi}",
        headers={"User-Agent": "cmt-most-site (mailto:bridge@metalab.ifmo.ru)"},
    )
    m = json.load(urllib.request.urlopen(req, timeout=30))["message"]
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
    dois = re.findall(r'doi: "https://doi\.org/([^"]+)"', DATA.read_text(encoding="utf-8"))
    known = {}
    if OUT.exists() and "--all" not in sys.argv:
        known = json.loads(OUT.read_text(encoding="utf-8")[len(HEADER):].rstrip().rstrip(";"))
    result = {}
    for doi in dois:
        if doi in known:
            result[doi] = known[doi]
            continue
        try:
            result[doi] = fetch(doi)
            print("скачано", doi)
        except Exception as e:  # публикация без записи в Crossref получит цитату из data.js
            print("нет данных", doi, e)
    OUT.write_text(HEADER + json.dumps(result, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8", newline="\n")
    print(f"готово, публикаций: {len(result)} из {len(dois)}")


main()
