"""Дописывает авторов публикациям, у которых их нет, по Crossref и OpenAlex.

Часть работ пришла на сайт без списка авторов: у переводных и конференционных записей
источник иногда отдает только название. Сначала спрашиваем Crossref, потом OpenAlex.
Что не нашлось нигде, скрипт перечисляет: такие работы владелец заполняет руками.

Запуск: python tools/fill_authors.py [--dry]
"""
import argparse
import json
import pathlib
import re
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "js" / "data.js"
UA = {"User-Agent": "cmt-most-site/1.0 (mailto:bridge@metalab.ifmo.ru)"}
NL = chr(10)


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as f:
            return json.load(f)
    except Exception:
        return {}


def from_crossref(doi):
    rows = (get("https://api.crossref.org/works/" + doi).get("message") or {}).get("author") or []
    names = [" ".join(x for x in (a.get("given"), a.get("family")) if x).strip() for a in rows]
    return [n for n in names if n]


def from_openalex(doi):
    rows = get("https://api.openalex.org/works/doi:" + doi).get("authorships") or []
    return [a["author"]["display_name"] for a in rows if (a.get("author") or {}).get("display_name")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    text = DATA.read_text(encoding="utf-8")
    body = text[text.index("window.PUBLICATIONS"):]
    filled, left = 0, []
    for block in re.findall(NL + "  [{].*?" + NL + "  [}],", body, re.S):
        got = re.search(r'authors: "([^"]*)"', block)
        if got and got.group(1).strip():
            continue
        title = (re.search(r'title: "(.*?)",' + NL, block, re.S) or [None, ""])[1]
        doi = (re.search(r'doi: "https://doi\.org/([^"]+)"', block) or [None, ""])[1]
        names = (from_crossref(doi) or from_openalex(doi)) if doi else []
        time.sleep(0.2)
        if not names:
            left.append((doi, title))
            continue
        line = ", ".join(names)
        if got:
            new = block.replace(got.group(0), 'authors: ' + json.dumps(line, ensure_ascii=False), 1)
        else:
            new = block.replace(NL + "    tags:", NL + "    authors: "
                                + json.dumps(line, ensure_ascii=False) + "," + NL + "    tags:", 1)
        text = text.replace(block, new, 1)
        filled += 1
        print("  " + title[:60] + " -> " + line[:70])

    print("дописано авторов: %d, осталось без авторов: %d" % (filled, len(left)))
    for doi, title in left:
        print("   %-38s %s" % (doi or "без DOI", title[:70]))
    if filled and not args.dry:
        DATA.write_text(text, encoding="utf-8", newline=NL)
        print("записано:", DATA)


main()
