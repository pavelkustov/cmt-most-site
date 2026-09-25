"""Переносит работы из content/collected/publications_db.json в список публикаций сайта.

Уже стоящие на сайте публикации не трогает: у них русские теги, описания, картинки
и направления, проставленные руками. Новые добавляются с пустым `direction`
(владелец расставит направления сам) и с английскими ключевыми словами в `tags`.

Не переносятся: помеченные дубли (препринт той же статьи, второй DOI той же работы),
а также записи, которые публикациями не являются: рецензии, наборы данных, отзывы статей.

Запуск: python tools/publications/to_site.py [--dry]
"""
import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib.paths import PUBLICATIONS, PUBLICATIONS_DB
from lib.store import load, rel, save
from publications.collect import STRANGERS   # работы однофамильцев, список ведется там

SKIP_TYPES = {"peer-review", "dataset", "retraction", "other", "dissertation"}
# уведомления о поправках и об озабоченности редакции: это не самостоятельные работы,
# на сайт они не идут (решение владельца, 21.09.2026)
NOTICE = re.compile(r"^\s*(correction|corrigendum|erratum|addendum|expression of concern|"
                    r"editorial expression|retraction note|publisher correction)\b", re.I)
# приложения к статьям: файл с данными на Figshare или Zenodo это не отдельная работа,
# у издателя он идет тем же типом «article» (решение владельца, 21.09.2026)
EXTRA = re.compile(r"^\s*(additional file|supplementary (material|information|data|file)|"
                   r"supporting information)\b", re.I)
CYR = re.compile(r"[а-яА-Я]")


def flat(title):
    return re.sub(r"[^0-9a-zа-я]+", "", (title or "").lower())


def doi_of(pub):
    return pub.get("doi", "").removeprefix("https://doi.org/").lower()


def retracted(rec):
    """Что на сайт не идет: отозванные работы, уведомления о поправках, приложения к статьям,
    а еще работы однофамильцев, которые остались в базе с прошлых сборов."""
    return (bool(rec["retracted"]) or rec["title"].upper().startswith("RETRACTED")
            or bool(NOTICE.match(rec["title"] or "")) or bool(EXTRA.match(rec["title"] or ""))
            or (rec["doi"] or "").lower() in STRANGERS or flat(rec["title"]) in STRANGERS)


def from_db(rec):
    """Новая публикация в том же виде, что остальные записи сайта."""
    pub = {"date": rec["date"] or (str(rec["year"]) if rec["year"] else ""), "journal": rec["journal"],
           "direction": [], "title": rec["title"], "authors": rec["authors"],
           "tags": rec["keywords_en"] or rec["topics"]}
    if rec["doi"]:
        pub["doi"] = "https://doi.org/" + rec["doi"]
    return pub


def carry_over(pub, gone):
    """Переносит ручную разметку с удаляемого дубля на остающуюся работу."""
    moved = []
    for name in ("quartile", "direction"):
        if gone.get(name) and not pub.get(name):
            pub[name] = gone[name]
            moved.append(name)
    if gone.get("desc") and not pub.get("desc"):
        pub["desc"] = gone["desc"]
        moved.append("desc")
    if CYR.search(" ".join(gone.get("tags", []))) and not CYR.search(" ".join(pub.get("tags", []))):
        pub["tags"] = gone["tags"]
        moved.append("теги")
    if moved:
        print("   перенесено на оставшуюся работу:", ", ".join(moved))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="только посчитать, файл не трогать")
    args = ap.parse_args()

    old = load(PUBLICATIONS)
    have_doi = {doi_of(p) for p in old if p.get("doi")}
    have_title = {flat(p["title"]) for p in old}

    db = load(PUBLICATIONS_DB)
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
            added.append(from_db(rec))

    # то, что в базе оказалось дублем или работой тезки, со страницы убираем
    bad = {r["doi"].lower() for r in db["works"] if (r["duplicate_of"] or retracted(r)) and r["doi"]}
    # у работ без DOI (русские оригиналы переводных статей) сверяем название, но только если
    # такого названия нет у оставленной записи: у дубля и у основной работы оно часто одно
    good_titles = {flat(r["title"]) for r in db["works"] if not r["duplicate_of"]}
    bad_titles = {flat(r["title"]) for r in db["works"] if r["duplicate_of"] and not r["doi"]} - good_titles
    twin = {}  # DOI оставшейся работы -> удаленный дубль с ручной разметкой
    by_doi = {r["doi"].lower(): r for r in db["works"] if r["doi"]}
    kept = []
    for p in old:
        doi = doi_of(p)
        if (doi and doi in bad) or flat(p["title"]) in bad_titles:
            print("убрана как отозванная:" if p["title"].upper().startswith("RETRACTED")
                  else "убрана как дубль:", (p["title"] or doi)[:70])
            twin[by_doi.get(doi, {}).get("duplicate_of", "").lower()] = p
            continue
        kept.append(p)

    result = sorted(kept + added, key=lambda p: p["date"], reverse=True)
    for p in result:
        if doi_of(p) and doi_of(p) in twin:
            carry_over(p, twin[doi_of(p)])
    print(f"было: {len(old)}, добавляется: {len(added)}, станет: {len(result)}")
    print("пропущено:", ", ".join(f"{k} {v}" for k, v in skipped.items() if v))
    if args.dry:
        return
    save(PUBLICATIONS, result)
    print("записано:", rel(PUBLICATIONS))
    print("дальше: python tools/publications/citations.py, потом python tools/smoke.py")


if __name__ == "__main__":
    main()
