"""Обновляет справочник сотрудников content/people.json по книге «ЦМТ Мост.xlsx» (папка data/book).

Из книги берутся только имя, степень или ступень обучения и должность. Почты, телефоны,
даты рождения и научные идентификаторы в репозиторий не переносятся.

Ключ в справочнике — «Имя Фамилия», в книге ФИО записано как «Фамилия Имя Отчество»,
поэтому имена приводятся к общему виду. Людей, которых в книге нет, скрипт не трогает
и перечисляет отдельно: их данные когда-то взяты из анкет направлений.

Запуск: python tools/people/book.py [--dry] [--book ПУТЬ]
"""
import argparse
import pathlib
import re
import sys

import openpyxl

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib.paths import BOOK, PEOPLE
from lib.store import load, rel, save


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
    people = load(PEOPLE)
    changed, missing = [], []
    for name, person in people.items():
        rec = book.get(name)
        if not rec:
            missing.append(name)
            continue
        was = dict(person)
        # ставим только непустые клетки: «не указано» в книге не затирает то, что назвал владелец
        for field in ("degree", "post"):
            if rec[field]:
                person[field] = rec[field]
        if person != was:
            changed.append((name, was, person))

    print(f"в книге людей: {len(book)}, в справочнике сайта: {len(people)}")
    for name, was, now in changed:
        bits = [f"{was.get(f, '')} -> {now[f]}" for f in ("degree", "post") if was.get(f, "") != now.get(f, "")]
        print(f"  {name}: " + "; ".join(bits))
    print(f"обновлено: {len(changed)}")
    if missing:
        print(f"в книге не нашлись ({len(missing)}), оставлены как были: " + ", ".join(missing))
    if changed and not args.dry:
        save(PEOPLE, people)
        print("записано:", rel(PEOPLE))
        print("дальше: python tools/texts/english.py --people (новые люди для английской версии) и python tools/smoke.py")


if __name__ == "__main__":
    main()
