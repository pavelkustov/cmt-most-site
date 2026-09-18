"""Переносит работы из docs/publications_db.json в window.PUBLICATIONS в data.js.

Уже стоящие на сайте публикации не трогает: у них русские теги, описания, картинки
и направления, проставленные руками. Новые добавляются с пустым `direction`
(владелец расставит направления сам) и с английскими ключевыми словами в `tags`.

Не переносятся: помеченные дубли (препринт той же статьи, второй DOI той же работы),
а также записи, которые публикациями не являются: рецензии, наборы данных, отзывы статей.

Запуск: python tools/publications_to_data.py [--dry]
"""
import argparse
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "js" / "data.js"
DB = ROOT / "docs" / "publications_db.json"
SKIP_TYPES = {"peer-review", "dataset", "retraction", "other", "dissertation"}


def js(value):
    """Строка или список строк в том виде, в каком они лежат в data.js."""
    if isinstance(value, list):
        return "[" + ", ".join(json.dumps(v, ensure_ascii=False) for v in value) + "]"
    return json.dumps(value, ensure_ascii=False)


def flat(title):
    return re.sub(r"[^0-9a-zа-я]+", "", (title or "").lower())


def blocks(text):
    """Куски вида «  {...},» из window.PUBLICATIONS, как они записаны в файле."""
    start = text.index("window.PUBLICATIONS = [") + len("window.PUBLICATIONS = [")
    end = text.index("\n];", start)
    return text[:start], re.findall(r"\n  \{.*?\n  \},", text[start:end], re.S), text[end:]


def block_of(rec):
    """Новая публикация в стиле остальных записей data.js."""
    tags = rec["keywords_en"] or rec["topics"]
    date = rec["date"] or (str(rec["year"]) if rec["year"] else "")
    lines = [
        f'    date: {js(date)}, journal: {js(rec["journal"])}, direction: [],',
        f'    title: {js(rec["title"])},',
        f'    authors: {js(rec["authors"])},',
        f'    tags: {js(tags)},',
    ]
    if rec["doi"]:
        lines.append(f'    doi: {js("https://doi.org/" + rec["doi"])},')
    return "\n  {\n" + "\n".join(lines) + "\n  },"


def sort_key(block):
    date = re.search(r'date: "([^"]*)"', block)
    return date.group(1) if date else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="только посчитать, файл не трогать")
    args = ap.parse_args()

    text = DATA.read_text(encoding="utf-8")
    head, old, tail = blocks(text)
    have_doi = {m.group(1).lower() for b in old for m in [re.search(r'doi: "https://doi\.org/([^"]+)"', b)] if m}
    have_title = {flat(m.group(1)) for b in old for m in [re.search(r'title: "(.*?)",\n', b, re.S)] if m}

    db = json.loads(DB.read_text(encoding="utf-8"))
    added, skipped = [], {"дубль": 0, "не публикация": 0, "уже на сайте": 0, "без названия": 0}
    for rec in db["works"]:
        if rec["duplicate_of"]:
            skipped["дубль"] += 1
        elif rec["type"] in SKIP_TYPES:
            skipped["не публикация"] += 1
        elif not rec["title"]:
            skipped["без названия"] += 1
        elif rec["doi"].lower() in have_doi or flat(rec["title"]) in have_title:
            skipped["уже на сайте"] += 1
        else:
            added.append(block_of(rec))

    result = sorted(old + added, key=sort_key, reverse=True)
    print(f"было: {len(old)}, добавляется: {len(added)}, станет: {len(result)}")
    print("пропущено:", ", ".join(f"{k} {v}" for k, v in skipped.items() if v))
    if args.dry:
        return
    DATA.write_text(head + "".join(result) + tail, encoding="utf-8", newline="\n")
    print("записано:", DATA)
    print("дальше: python tools/fetch_citations.py, потом tools/smoke.py")


main()
