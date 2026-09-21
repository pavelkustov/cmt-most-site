"""Уточняет даты публикаций в data.js по Crossref.

У части работ в базе стоит только год или год с месяцем: OpenAlex отдает дату так,
как ее записал издатель в момент выкладки. Crossref знает точнее: у него есть дата выпуска
номера (published-print) и дата публикации онлайн (published-online). Берем самую полную,
предпочитая дату выпуска: именно она стоит на странице статьи у издателя.

Запуск: python tools/fix_dates.py [--dry] [--all]
По умолчанию правятся только неполные даты. С --all сверяются все работы с DOI,
расхождения печатаются, но не применяются без подтверждения глазами.
"""
import argparse
import hashlib
import json
import pathlib
import re
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "js" / "data.js"
CACHE = pathlib.Path(tempfile.gettempdir()) / "cmt_most_dates"
MANUAL = ROOT / "docs" / "dates_manual.json"    # даты, вписанные владельцем
MISSING = ROOT / "docs" / "DATES_MISSING.md"    # работы, у которых даты не хватает
LINKS = ROOT / "docs" / "publication_links.json"  # ссылки на работы без DOI
UA = {"User-Agent": "cmt-most-site/1.0 (mailto:bridge@metalab.ifmo.ru)"}
NL = chr(10)


def crossref(doi):
    box = CACHE / (hashlib.sha1(doi.encode()).hexdigest() + ".json")
    if box.exists():
        return json.loads(box.read_text(encoding="utf-8"))
    try:
        with urllib.request.urlopen(
                urllib.request.Request("https://api.crossref.org/works/" + doi, headers=UA), timeout=45) as f:
            data = json.load(f)["message"]
    except Exception:
        data = {}
    CACHE.mkdir(exist_ok=True)
    box.write_text(json.dumps(data), encoding="utf-8")
    time.sleep(0.2)
    return data


def as_date(part):
    """«date-parts» Crossref в вид 2026-12-15, насколько хватает точности."""
    bits = ((part or {}).get("date-parts") or [[]])[0]
    if not bits:
        return ""
    return "-".join(str(b).zfill(2) if i else str(b) for i, b in enumerate(bits))


def best_date(rec):
    """Дата выпуска номера важнее даты выкладки онлайн: ее показывает издатель."""
    for key in ("published-print", "issued", "published-online", "published"):
        got = as_date(rec.get(key))
        if len(got) == 10:
            return got
    return ""


MONTHS = {m: i + 1 for i, m in enumerate(
    "january february march april may june july august september october november december".split())}
MONTHS.update({m: i + 1 for i, m in enumerate(
    "januar februar mart aprel maj ijun ijul avgust sentjabr oktjabr nojabr dekabr".split())})
MONTHS_RU = {m: i + 1 for i, m in enumerate(
    "январ феврал март апрел ма июн июл август сентябр октябр ноябр декабр".split())}


def parse_date(text):
    """Понимает 15.12.2026, 2026-12-15 и «15 December 2026», как пишут издатели."""
    text = text.strip().strip("_ ").lower()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", text)
    if m:
        return text
    m = re.match(r"^(\d{1,2})[.](\d{1,2})[.](\d{4})$", text)
    if m:
        return "%s-%s-%s" % (m.group(3), m.group(2).zfill(2), m.group(1).zfill(2))
    m = re.match(r"^([a-zа-я]+)\s+(\d{1,2}),?\s+(\d{4})$", text)   # «April 24, 2013»
    if m:
        word = m.group(1)
        num = MONTHS.get(word) or next((v for k, v in MONTHS_RU.items() if word.startswith(k)), 0)
        if num:
            return "%s-%s-%s" % (m.group(3), str(num).zfill(2), m.group(2).zfill(2))
    m = re.match(r"^(\d{1,2})\s+([a-zа-я]+),?\s+(\d{4})$", text)
    if m:
        word = m.group(2)
        num = MONTHS.get(word) or next((v for k, v in MONTHS_RU.items() if word.startswith(k)), 0)
        if num:
            return "%s-%s-%s" % (m.group(3), str(num).zfill(2), m.group(1).zfill(2))
    return ""


def flat(title):
    """Ключ для работы без DOI: у нее нет ссылки, опознаем по названию."""
    return "title:" + re.sub(r"[^0-9a-zа-я]+", "", (title or "").lower())[:60]


def load_manual():
    if not MANUAL.exists():
        return {}
    return {k.lower(): v for k, v in json.loads(MANUAL.read_text(encoding="utf-8")).items() if v.strip()}


def load_links():
    if not LINKS.exists():
        return {}
    return {k.lower(): v for k, v in json.loads(LINKS.read_text(encoding="utf-8")).items() if v.strip()}


def filled_already(section):
    """То, что владелец уже вписал в список: при перегенерации это не теряется."""
    if not MISSING.exists():
        return {}
    out = {}
    for chunk in MISSING.read_text(encoding="utf-8").split(NL + "## ")[1:]:
        doi = re.search(r"<!-- doi: ([^\s]+) -->", chunk)
        body = re.search("### " + section + NL + "(.*?)$", chunk, re.S)
        if not doi or not body:
            continue
        text = body.group(1).strip()
        if text and not text.startswith("_впишите"):
            out[doi.group(1).lower()] = text
    return out


def write_missing(rows):
    """Список работ с неполной датой: владелец смотрит страницу статьи и вписывает день."""
    kept = filled_already("Дата")
    out = ["# Работы с неполной датой", "",
           "У этих работ в дате нет дня, а иногда и месяца: так их отдают OpenAlex и Crossref.",
           "Полная дата обычно стоит на странице статьи у издателя, например «15 December 2026».",
           "Откройте ссылку и впишите дату под заголовком «Дата», вместо строки-подсказки.",
           "Понимаются три формата: 15.12.2026, 2026-12-15 и 15 December 2026.", "",
           "Потом: `python tools/fix_dates.py --import-md` перенесет даты",
           "в `docs/dates_manual.json` и проставит их в `data.js`.", "",
           f"Всего работ: {len(rows)}", ""]
    for doi, date, title, journal in rows:
        out.append("## " + (title or "без названия"))
        out.append("")
        out.append("<!-- doi: " + (doi or flat(title)) + " -->")
        out.append("")
        out.append("%s. Сейчас на сайте: %s" % (journal or "издание не указано", date))
        out.append("")
        out.append("https://doi.org/" + doi if doi
                   else "DOI у работы нет, искать по названию в поиске издателя или в eLibrary")
        out.append("")
        out.append("### Дата")
        out.append("")
        out.append(kept.get(doi.lower(), "_впишите сюда_"))
        out.append("")
    MISSING.write_text(NL.join(out).rstrip() + NL, encoding="utf-8", newline=NL)
    print(f"список для ручного добора: {MISSING} ({len(rows)} работ)")


def import_md():
    """Забирает даты из docs/DATES_MISSING.md в docs/dates_manual.json.

    Владелец дописывает в файл свои заголовки, например «## ССЫЛКА: ...», поэтому идем
    по разделам подряд и держим последнюю встреченную работу, а не разбираем каждый кусок
    отдельно. Ссылки на статьи тоже забираем: у работ без DOI это единственный адрес,
    по которому их можно открыть.
    """
    if not MISSING.exists():
        print("нет файла", MISSING)
        return {}, {}
    manual, links, bad = load_manual(), load_links(), []
    key = ""
    for chunk in MISSING.read_text(encoding="utf-8").split(NL + "## ")[1:]:
        doi = re.search(r"<!-- doi: ([^\s]+) -->", chunk)
        if doi:
            key = doi.group(1).lower()
        link = re.search(r"ССЫЛКА:\s*(\S+)", chunk)
        if link and key:
            links[key] = link.group(1).strip()
        body = re.search(r"### Дата" + NL + "(.*?)$", chunk, re.S)
        if not body or not key:
            continue
        lines = [x.strip() for x in body.group(1).splitlines() if x.strip()]
        raw = lines[0] if lines else ""
        if not raw or raw.startswith("_впишите"):
            continue
        date = parse_date(raw)
        if date:
            manual[key] = date
        else:
            bad.append((key, raw[:60]))
    MANUAL.write_text(json.dumps(manual, ensure_ascii=False, indent=1, sort_keys=True),
                      encoding="utf-8", newline=NL)
    LINKS.write_text(json.dumps(links, ensure_ascii=False, indent=1, sort_keys=True),
                     encoding="utf-8", newline=NL)
    print("дат вписано руками: %d, ссылок на работы без DOI: %d" % (len(manual), len(links)))
    for key, raw in bad:
        print("  не понял дату «%s» у %s" % (raw, key))
    return manual, links


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--all", action="store_true", help="сверить все работы, а не только неполные даты")
    ap.add_argument("--import-md", dest="import_md", action="store_true",
                    help="забрать даты из docs/DATES_MISSING.md и проставить их")
    ap.add_argument("--offline", action="store_true", help="не ходить в Crossref, только ручные даты")
    args = ap.parse_args()

    manual, links = import_md() if args.import_md else (load_manual(), load_links())
    text = DATA.read_text(encoding="utf-8")
    blocks = re.findall(r"\n  \{.*?\n  \},", text[text.index("window.PUBLICATIONS"):], re.S)
    fixed, by_hand, differ, absent, rows = 0, 0, [], 0, []
    for block in blocks:
        date = re.search(r'date: "([^"]*)"', block)
        doi = re.search(r'doi: "https://doi[\.]org/([^"]+)"', block)
        if not date:
            continue
        title = (re.search(r'title: "(.*?)",' + NL, block, re.S) or [None, ""])[1]
        key = doi.group(1).lower() if doi else flat(title)
        journal = (re.search(r'journal: "([^"]*)"', block) or [None, ""])[1]

        if manual.get(key) and manual[key] != date.group(1):
            text = text.replace(block, block.replace('date: "' + date.group(1) + '"',
                                                     'date: "' + manual[key] + '"'), 1)
            by_hand += 1
            continue
        if len(date.group(1)) == 10 and not args.all:
            continue

        got = "" if (args.offline or not doi) else best_date(crossref(doi.group(1)))
        # день подставляем только внутри того же месяца: иначе это дата выкладки онлайн,
        # она уводит работу в другой месяц или год и ломает порядок на странице
        if got and len(date.group(1)) < 10 and got.startswith(date.group(1)):
            text = text.replace(block, block.replace('date: "' + date.group(1) + '"',
                                                     'date: "' + got + '"'), 1)
            fixed += 1
            print("  %s -> %s  %s" % (date.group(1), got, title[:60]))
            continue
        if got:
            differ.append((date.group(1), got, title[:60]))
        else:
            absent += 1
        if len(date.group(1)) < 10:
            rows.append((doi.group(1) if doi else "", date.group(1), title, journal))

    print("уточнено по Crossref: %d, вписано руками: %d, у Crossref даты нет: %d" % (fixed, by_hand, absent))
    if differ:
        print("расходятся с Crossref, но не тронуты (%d), это чаще всего дата выкладки онлайн:" % len(differ))
        for was, now, title in differ[:40]:
            print("  %s против %s  %s" % (was, now, title))
    if (fixed or by_hand) and not args.dry:
        DATA.write_text(text, encoding="utf-8", newline=NL)
        print("записано:", DATA)
        print("дальше: python tools/bump_assets.py и python tools/smoke.py")
    if rows and not args.dry:
        write_missing(rows)


main()
