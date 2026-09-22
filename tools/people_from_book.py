"""Обновляет справочник сотрудников window.PEOPLE в data.js по книге «ЦМТ Мост.xlsx».

Из книги берутся только имя, степень или ступень обучения и должность. Почты, телефоны,
даты рождения и научные идентификаторы в репозиторий не переносятся.

Ключ в data.js — «Имя Фамилия», в книге ФИО записано как «Фамилия Имя Отчество»,
поэтому имена приводятся к общему виду. Людей, которых в книге нет, скрипт не трогает
и перечисляет отдельно: их данные когда-то взяты из анкет направлений.

Запуск: python tools/people_from_book.py [--dry] [--book ПУТЬ]
"""
import argparse
import json
import pathlib
import re
import sys

import openpyxl

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sources import BOOK  # книга лежит в data/book, путь ведет общий модуль

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "js" / "data.js"
NL = chr(10)


def short_name(full):
    """«Зюзин Михаил Валерьевич» -> «Михаил Зюзин», как принято в данных сайта."""
    parts = re.sub(r"\s+", " ", (full or "").strip()).split(" ")
    if len(parts) < 2:
        return ""
    return parts[1] + " " + parts[0]


def clean(value):
    """Пустая клетка и «не указано» в книге значат одно: данных нет, на сайт не несем."""
    value = re.sub(r"\s+", " ", str(value or "").strip())
    return "" if value.lower() in ("", "не указано", "-", "нет") else value


def read_book(path):
    sheet = openpyxl.load_workbook(path, data_only=True)["Сотрудники центра"]
    rows = {}
    for row in sheet.iter_rows(min_row=2, values_only=True):
        name = short_name(row[1])
        if name:
            rows[name] = {"degree": clean(row[3]), "post": clean(row[4])}
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--book", default=str(BOOK))
    args = ap.parse_args()

    book = read_book(args.book)
    text = DATA.read_text(encoding="utf-8")
    start = text.index("window.PEOPLE = {")
    end = text.index(NL + "};", start)
    block, changed, missing = text[start:end], [], []

    for line in re.findall(r'  "[^"]+": \{[^}]*\},', block):
        name = re.search(r'"([^"]+)"', line).group(1)
        rec = book.get(name)
        if not rec:
            missing.append(name)
            continue
        was_degree = (re.search(r'degree: "([^"]*)"', line) or [None, ""])[1]
        was_post = (re.search(r'post: "([^"]*)"', line) or [None, ""])[1]
        new = line
        if rec["degree"] and rec["degree"] != was_degree:
            new = new.replace(f'degree: "{was_degree}"', "degree: " + json.dumps(rec["degree"], ensure_ascii=False))
        if rec["post"] and rec["post"] != was_post:
            new = new.replace(f'post: "{was_post}"', "post: " + json.dumps(rec["post"], ensure_ascii=False))
        if new != line:
            changed.append((name, was_degree, rec["degree"], was_post, rec["post"]))
            block = block.replace(line, new, 1)

    print(f"в книге людей: {len(book)}, в справочнике сайта: {block.count(': {')}")
    for name, d0, d1, p0, p1 in changed:
        bits = []
        if d0 != d1:
            bits.append(f"{d0} -> {d1}")
        if p0 != p1:
            bits.append(f"{p0} -> {p1}")
        print(f"  {name}: " + "; ".join(bits))
    print(f"обновлено: {len(changed)}")
    if missing:
        print(f"в книге не нашлись ({len(missing)}), оставлены как были: " + ", ".join(missing))
    if changed and not args.dry:
        DATA.write_text(text[:start] + block + text[end:], encoding="utf-8", newline=NL)
        print("записано:", DATA)
        print("дальше: python tools/bump_assets.py и python tools/smoke.py")


main()
