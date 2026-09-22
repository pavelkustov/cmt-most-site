"""Переносит новости из анкеты «011_Новости.docx» в window.NEWS в data.js.

Анкету заполняет владелец: одна таблица на новость, в желтой колонке новое значение.
Метка в первой колонке говорит, куда значение идет: [news:ид.поле] правит новость,
которая уже на сайте, [newnews:номер.поле] заводит новую.

Разобранные новости лежат в docs/news.json, это источник правды: анкету владелец
переписывает, а json помнит все, что уже перенесено. Фотографии хранятся там же
в полях image и popupImage, поэтому перенос текстов их не затирает.

Запуск: python tools/news_from_form.py [--dry] [--form ПУТЬ]
"""
import argparse
import datetime
import json
import pathlib
import re
import shutil
import tempfile

import docx

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "js" / "data.js"
STORE = ROOT / "docs" / "news.json"
FORM = ROOT.parent / "011_Новости.docx"
NL = chr(10)

# Адрес новости в ссылке вида news.html?open=..., поэтому имя короткое и латинское.
# Ключ — номер таблицы в анкете, он же номер новости в метке [newnews:номер].
SLUGS = {
    1: "iclo-2026", 2: "liver-mirna", 3: "lumos-2026", 4: "biomaterials-paper",
    5: "itmo-collab-2026", 6: "holoexpo-2025", 7: "ciop-2025", 8: "knvsh-2025",
    9: "yali-interview", 10: "everest-2025", 11: "meng-su-visit", 12: "flamn-25-award",
    13: "flamn-25", 14: "nature-comms-2025", 15: "yali-sun-hust", 16: "zmaga-hust",
    17: "tv-spb-2026", 18: "phd-finish-2026", 19: "nlp-school-2026", 20: "valiev-scholarship",
    21: "photonics-expo-2025", 22: "nanophysics-2025", 23: "melchakova-join",
    24: "ponkratova-phd", 25: "biophotonics-school-2024", 26: "metanano-2024",
    27: "cust-course-2025", 28: "eastmag-2025", 29: "spie-cos-2024", 30: "alt-2024",
    31: "microelectronics-2024", 32: "holoexpo-2024", 33: "rosupack-2024",
    34: "school-projects-2024", 35: "harbin-seminar-2024", 36: "conferences-2023",
    37: "larin-phd", 38: "new-phd-students-2023", 39: "physics-course-2023",
    40: "yaroshenko-phd", 41: "unclonable-labels-2023", 42: "unclonix-gitex-2023",
}

# Новости, которые владелец пока не выкладывает.
SKIP = {}

# Даты, которые в анкете стоят неверно. Решения владельца от 22.09.2026.
DATES = {
    9: "2025-08-21",   # в ячейке даты стоит заголовок, день назвал владелец
    24: "2024-12-25",  # в анкете 25.12.2015, Понкратова защитилась в 2024
    35: "2024-04-29",  # в ячейке даты повторен заголовок, семинар шел 26–29 апреля 2024
}

# Таблицы, где владелец заполнял анкету со сдвигом на строку: заголовок попал в дату
# и дальше все съехало. Ключ это поле новости, значение это откуда его брать в анкете,
# список означает склейку нескольких ячеек по порядку.
SHIFT = {
    9: {"title": "date", "text": "title", "lead": ["text", "lead"]},
}

# Пометки владельца в ячейке фотографии. Именем файла не являются, на сайт не идут.
NOTES = ("link", "жду от лены", "нет", "-")

# Сколько знаков помещается в карточку: заголовок три строки, анонс пять (см. style.css)
TITLE_MAX = 70
TEXT_MAX = 225

# Заголовки, переписанные для сайта. Ведет их tools/news_titles.py, здесь они побеждают анкету:
# в анкете заголовок пишут как удобно, а на карточке он должен читаться как в газете
TITLES = ROOT / "docs" / "news_titles.json"

# Описки в анкете и единообразие написания. Тексты владельца не переписываем, правим только
# явные склейки слов, прямые кавычки и название центра: на сайте он везде ЦМТ «Мост».
TYPOS = {
    "«МОСТ»мприняла": "«Мост» приняла",
    "ЦМТ «МОСТ»": "ЦМТ «Мост»",
    'ЦМТ "МОСТ"': "ЦМТ «Мост»",
    'ЦМТ "Мост"': "ЦМТ «Мост»",
    # кавычки внутри кавычек ставим лапками, порядок замен важен: сперва открывающая
    "\u201c": "\u201e",
    "\u201d": "\u201c",
}


def ye(text):
    """На сайте букву «ё» не пишем, описки из анкеты чиним по списку."""
    text = text.replace("ё", "е").replace("Ё", "Е")
    for was, now in TYPOS.items():
        text = text.replace(was, now)
    return text


def paras(cell_text):
    """Абзацы ячейки: в анкете они разделены переводом строки."""
    return [ye(re.sub(r"\s+", " ", p).strip()) for p in cell_text.split(NL) if p.strip()]


def one(cell_text):
    return " ".join(paras(cell_text))


def as_date(value):
    """«29.06.2026» и «26.08.2026.» -> «2026-06-29». Непонятное возвращает пустым."""
    m = re.match(r"(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})", value.strip())
    if not m:
        return ""
    day, month, year = (int(x) for x in m.groups())
    try:
        return datetime.date(year, month, day).isoformat()
    except ValueError:
        return ""


def read_form(path):
    """Желтая колонка анкеты: (номер таблицы, метка, заполненные поля) по порядку.

    Номер новости берем по порядку таблиц, а не из метки: владелец заводит новость
    копией последней таблицы, и номер в метке у копий остается прежним.
    """
    # Word держит открытый документ заблокированным, поэтому читаем копию
    with tempfile.TemporaryDirectory() as tmp:
        copy = pathlib.Path(tmp) / "form.docx"
        shutil.copy2(path, copy)
        doc = docx.Document(str(copy))
        rows = []
        for number, table in enumerate(doc.tables):
            mark, fields = "", {}
            for row in table.rows[1:]:
                cells = row.cells
                key = re.search(r"\[([^\]]+)\]", cells[0].text)
                if not key or len(cells) < 3:
                    continue
                mark, field = key.group(1).rsplit(".", 1)
                value = cells[2].text.strip()
                if value:
                    fields[field] = value
            if mark:
                rows.append((number, mark, fields))
    return rows


def photo_of(value):
    """Имя файла из ячейки фотографии. Пометки вроде «link» фотографией не считаются."""
    value = value.strip()
    if value.lower() in NOTES or not re.search(r"\.(webp|jpg|jpeg|png)$", value, re.I):
        return ""
    return value


def unshift(fields, plan):
    """Раскладывает съехавшие ячейки анкеты по своим полям (см. SHIFT)."""
    out = {k: v for k, v in fields.items() if k not in plan and k not in sum(
        ([x] if isinstance(x, str) else x for x in plan.values()), [])}
    for field, source in plan.items():
        parts = [fields.get(s, "") for s in ([source] if isinstance(source, str) else source)]
        value = NL.join(p for p in parts if p.strip())
        if value:
            out[field] = value
    return out


def apply(record, fields):
    """Накладывает заполненные ячейки на запись новости. УДАЛИТЬ стирает значение."""
    body = record.setdefault("body", {})
    for field, value in fields.items():
        erase = value.strip().upper() == "УДАЛИТЬ"
        if field == "date":
            iso = as_date(value)
            if iso:
                record["date"] = iso
        elif field in ("tag", "title", "text"):
            record[field] = "" if erase else one(value)
        elif field in ("lead", "note"):
            body.pop(field, None) if erase else body.update({field: paras(value)})
        elif field == "quote":
            body.pop("quote", None) if erase else body.update({"quote": paras(value)})
        elif field == "photo":
            name = photo_of(value)
            if erase:
                record.pop("image", None)
                record.pop("popupImage", None)
            elif name:
                record["image"] = name
        elif field == "featured":
            record["featured"] = not erase and value.strip().lower() in ("да", "yes")
    if not body:
        record.pop("body", None)
    return record


def js_news(items):
    """window.NEWS так, как он лежит в data.js: поля в одном порядке, тексты по строкам."""
    out = []
    for n in items:
        head = [f'id: {json.dumps(n["id"], ensure_ascii=False)}']
        if n.get("featured"):
            head.append("featured: true")
        head += [f'tag: {json.dumps(n["tag"], ensure_ascii=False)}',
                 f'date: {json.dumps(n["date"], ensure_ascii=False)}']
        for key in ("image", "popupImage"):
            if n.get(key):
                head.append(f'{key}: {json.dumps(n[key], ensure_ascii=False)}')
        lines = ["  {", "    " + ", ".join(head) + ",",
                 f'    title: {json.dumps(n["title"], ensure_ascii=False)},',
                 f'    text: {json.dumps(n["text"], ensure_ascii=False)},']
        body = n.get("body") or {}
        if body:
            lines.append("    body: {")
            for key in ("lead", "quote", "note"):
                if not body.get(key):
                    continue
                lines.append(f"      {key}: [")
                lines += [f"        {json.dumps(p, ensure_ascii=False)}," for p in body[key]]
                lines.append("      ],")
            lines.append("    },")
        lines.append("  },")
        out += lines
    return NL.join(out)


def in_order(items):
    """Новости всегда лежат от свежих к старым, и наверху страницы самая свежая.

    Порядок задается здесь, а не в вызывающем коде: дату правят и из других скриптов,
    и без общей сортировки карточка оставалась бы на прежнем месте.
    """
    rows = sorted(items, key=lambda n: n["date"], reverse=True)
    for n in rows:
        n["featured"] = n is rows[0]
    return rows


def write_js(items):
    """Переписывает window.NEWS в data.js по разобранному списку."""
    text = DATA.read_text(encoding="utf-8")
    start = text.index("window.NEWS = [") + len("window.NEWS = [")
    end = text.index(NL + "];", start)
    DATA.write_text(text[:start] + NL + js_news(in_order(items)) + text[end:],
                    encoding="utf-8", newline=NL)


def write_store(items):
    STORE.write_text(json.dumps(in_order(items), ensure_ascii=False, indent=1) + NL,
                     encoding="utf-8", newline=NL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--form", default=str(FORM))
    args = ap.parse_args()

    store = json.loads(STORE.read_text(encoding="utf-8")) if STORE.exists() else []
    titles = json.loads(TITLES.read_text(encoding="utf-8")) if TITLES.exists() else {}
    by_id = {n["id"]: n for n in store}
    added, changed, left, marked = [], [], [], set()

    for number, mark, fields in read_form(args.form):
        kind, key = mark.split(":", 1)
        if fields.get("featured", "").strip().lower() in ("да", "yes"):
            marked.add(key if kind == "news" else SLUGS.get(number, ""))
        if kind == "news":
            if key in by_id and fields:
                apply(by_id[key], fields)
                changed.append(key)
            continue
        if number in SKIP:
            left.append(f"новость {number}: " + SKIP[number])
            continue
        if not fields:
            continue
        slug = SLUGS.get(number)
        if not slug:
            left.append(f"новость {number}: нет короткого имени в SLUGS, "
                        f"заголовок «{one(fields.get('title', ''))[:60]}»")
            continue
        record = by_id.get(slug, {"id": slug})
        was = json.dumps(record, ensure_ascii=False, sort_keys=True)
        if number in SHIFT:
            fields = unshift(fields, SHIFT[number])
        apply(record, fields)
        # номер таблицы в анкете: по нему tools/news_photos.py раскладывает фотографии
        record["form"] = number
        if number in DATES:
            record["date"] = DATES[number]
        if not record.get("date") or not record.get("title"):
            left.append(f"новость {number} ({slug}): нет даты или заголовка")
            continue
        record.setdefault("tag", "Событие")
        # заголовок из анкеты помним отдельно, на сайте стоит переписанный
        record["formTitle"] = record["title"]
        if slug in by_id:
            if json.dumps(record, ensure_ascii=False, sort_keys=True) != was:
                changed.append(slug)
        else:
            by_id[slug] = record
            added.append(slug)

    # переписанные заголовки побеждают анкету, оригинал остается в поле formTitle
    for n in by_id.values():
        if titles.get(n["id"]) and titles[n["id"]] != n["title"]:
            n.setdefault("formTitle", n["title"])
            n["title"] = titles[n["id"]]

    items = sorted(by_id.values(), key=lambda n: n["date"], reverse=True)
    # Новость месяца стоит крупно наверху страницы. Наверх идет самая свежая, иначе список
    # растет, а наверху висит старая новость. Отметка в анкете это правило перебивает.
    top = next((n for n in items if n["id"] in marked), items[0])
    for n in items:
        n["featured"] = n is top

    # в карточке под заголовок отведено три строки, под анонс пять: что длиннее,
    # обрезается многоточием. Меры взяты из стилей, их же просит анкета.
    # Маркеры переноса в счет не идут, это разметка, а не текст
    plain = lambda s: re.sub(r"\s*<\s*/?\s*br\s*/?\s*>\s*", " ", s)
    long_title = [n["id"] for n in items if len(plain(n["title"])) > TITLE_MAX]
    long_text = [n["id"] for n in items if len(n.get("text", "")) > TEXT_MAX]

    print(f"новостей: {len(items)}, добавлено: {len(added)}, изменено: {len(set(changed))}")
    if added:
        print("  добавлены: " + ", ".join(added))
    if set(changed):
        print("  изменены: " + ", ".join(sorted(set(changed))))
    print("  новость месяца: " + top["title"][:60])
    no_photo = [n["id"] for n in items if not n.get("image")]
    if no_photo:
        print(f"  без фотографии ({len(no_photo)}): " + ", ".join(no_photo))
    if long_title:
        print(f"  заголовок не влезет в карточку, обрежется ({len(long_title)}): "
              + ", ".join(long_title))
    if long_text:
        print(f"  анонс не влезет в карточку, обрежется ({len(long_text)}): "
              + ", ".join(long_text))
    for line in left:
        print("  не перенесено: " + line)

    if args.dry:
        print("сухой прогон, файлы не тронуты")
        return
    write_store(items)
    write_js(items)
    print("записано:", STORE.name, "и", DATA.name)
    print("дальше: python tools/bump_assets.py и python tools/smoke.py")


if __name__ == "__main__":
    main()
