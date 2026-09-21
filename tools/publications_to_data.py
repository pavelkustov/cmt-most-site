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
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fetch_publications import STRANGERS   # работы однофамильцев, список ведется там

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "js" / "data.js"
DB = ROOT / "docs" / "publications_db.json"
SKIP_TYPES = {"peer-review", "dataset", "retraction", "other", "dissertation"}
# уведомления о поправках и об озабоченности редакции: это не самостоятельные работы,
# на сайт они не идут (решение владельца, 21.09.2026)
NOTICE = re.compile(r"^\s*(correction|corrigendum|erratum|addendum|expression of concern|"
                    r"editorial expression|retraction note|publisher correction)\b", re.I)
# приложения к статьям: файл с данными на Figshare или Zenodo это не отдельная работа,
# у издателя он идет тем же типом «article» (решение владельца, 21.09.2026)
EXTRA = re.compile(r"^\s*(additional file|supplementary (material|information|data|file)|"
                   r"supporting information)\b", re.I)


def retracted(rec):
    """Что на сайт не идет: отозванные работы, уведомления о поправках, приложения к статьям,
    а еще работы однофамильцев, которые остались в базе с прошлых сборов."""
    return (bool(rec["retracted"]) or rec["title"].upper().startswith("RETRACTED")
            or bool(NOTICE.match(rec["title"] or "")) or bool(EXTRA.match(rec["title"] or ""))
            or (rec["doi"] or "").lower() in STRANGERS or flat(rec["title"]) in STRANGERS)


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


def field(block, name):
    """Значение поля записи data.js: строка в кавычках или список."""
    m = re.search(name + r': (\[[^\]]*\]|"(?:[^"\\]|\\.)*")', block, re.S)
    return m.group(1) if m else ""


def carry_over(block, gone):
    """Переносит ручную разметку с удаляемого дубля на остающуюся работу."""
    moved = []
    for name in ("quartile", "direction"):
        theirs, mine = field(gone, name), field(block, name)
        if theirs and theirs not in ('""', "[]") and mine in ("", '""', "[]"):
            if mine:
                block = block.replace(f"{name}: {mine}", f"{name}: {theirs}")
            else:  # поля нет вовсе, дописываем в строку с датой
                block = block.replace("direction:", f"{name}: {theirs}, direction:", 1)
            moved.append(name)
    desc = field(gone, "desc")
    if desc and not field(block, "desc"):
        block = block.replace("\n    tags:", f"\n    desc: {desc},\n    tags:", 1)
        moved.append("desc")
    tags = field(gone, "tags")
    if re.search(r"[а-яА-Я]", tags) and not re.search(r"[а-яА-Я]", field(block, "tags")):
        block = block.replace(f"tags: {field(block, 'tags')}", f"tags: {tags}", 1)
        moved.append("теги")
    if moved:
        print("   перенесено на оставшуюся работу:", ", ".join(moved))
    return block


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
    added, skipped = [], {"дубль": 0, "не публикация": 0, "отозвана": 0,
                          "уже на сайте": 0, "без названия": 0}
    for rec in db["works"]:
        if rec["duplicate_of"]:
            skipped["дубль"] += 1
        elif retracted(rec):
            skipped["отозвана"] += 1
        elif rec["type"] in SKIP_TYPES:
            skipped["не публикация"] += 1
        elif not rec["title"]:
            skipped["без названия"] += 1
        elif rec["doi"].lower() in have_doi or flat(rec["title"]) in have_title:
            skipped["уже на сайте"] += 1
        else:
            added.append(block_of(rec))

    # то, что в базе оказалось дублем или работой тезки, со страницы убираем
    bad = {r["doi"].lower() for r in db["works"] if (r["duplicate_of"] or retracted(r)) and r["doi"]}
    # у работ без DOI (русские оригиналы переводных статей) сверяем название, но только если
    # такого названия нет у оставленной записи: у дубля и у основной работы оно часто одно
    good_titles = {flat(r["title"]) for r in db["works"] if not r["duplicate_of"]}
    bad_titles = {flat(r["title"]) for r in db["works"]
                  if r["duplicate_of"] and not r["doi"]} - good_titles
    twin = {}  # DOI оставшейся работы -> разметка удаленного дубля
    by_doi = {r["doi"].lower(): r for r in db["works"] if r["doi"]}
    kept = []
    for b in old:
        doi = re.search(r'doi: "https://doi\.org/([^"]+)"', b)
        title = re.search(r'title: "(.*?)",\n', b, re.S)
        if (doi and doi.group(1).lower() in bad) or (title and flat(title.group(1)) in bad_titles):
            name = (title.group(1) if title else doi.group(1))[:70]
            print("убрана как отозванная:" if name.upper().startswith("RETRACTED")
                  else "убрана как дубль:", name)
            main = by_doi.get(doi.group(1).lower(), {}).get("duplicate_of", "") if doi else ""
            twin[main.lower()] = b
            continue
        kept.append(b)

    result = sorted(kept + added, key=sort_key, reverse=True)
    if twin:
        for i, b in enumerate(result):
            doi = re.search(r'doi: "https://doi\.org/([^"]+)"', b)
            if doi and doi.group(1).lower() in twin:
                result[i] = carry_over(b, twin[doi.group(1).lower()])
    print(f"было: {len(old)}, добавляется: {len(added)}, станет: {len(result)}")
    print("пропущено:", ", ".join(f"{k} {v}" for k, v in skipped.items() if v))
    if args.dry:
        return
    DATA.write_text(head + "".join(result) + tail, encoding="utf-8", newline="\n")
    print("записано:", DATA)
    print("дальше: python tools/fetch_citations.py, потом tools/smoke.py")


main()
