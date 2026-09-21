"""Собирает авторские абстракты публикаций в assets/js/abstracts.js.

Абстракт берется как он есть у издателя, на языке статьи, и не переводится.
Источники: docs/publications_db.json (там абстракты из OpenAlex) и Crossref по DOI
для тех работ, у которых в базе абстракта нет. Crossref отдает его разметкой JATS,
теги вычищаются, абзацы сохраняются.

Файл получается вида window.ABSTRACTS = {"10.1021/...": "текст"} и подключается
на страницах со списками публикаций.

Запуск: python tools/fetch_abstracts.py [--no-crossref] [--limit N]
"""
import argparse
import html
import hashlib
import json
import pathlib
import re
import tempfile
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = ROOT / "docs" / "publications_db.json"
DATA = ROOT / "assets" / "js" / "data.js"
OUT = ROOT / "assets" / "js" / "abstracts.js"
MANUAL = ROOT / "docs" / "abstracts_manual.json"   # абстракты, вписанные владельцем
MISSING = ROOT / "docs" / "ABSTRACTS_MISSING.md"   # список работ, которым абстракта не нашлось
UA = {"User-Agent": "cmt-most-site/1.0 (mailto:bridge@metalab.ifmo.ru)"}
NL = chr(10)
CACHE = pathlib.Path(tempfile.gettempdir()) / "cmt_most_abstracts"
NO_NET = []   # непустой при --offline: тогда живем на том, что уже в кэше

# работы, у которых абстракта нет и не будет: в список для ручного добора их не выносим
NO_ABSTRACT = {
    "10.1016/s0969-8051(21)00408-x": "тезисы конференции, абстракта нет (проверено владельцем)",
}

JUNK = re.compile(r"^\s*(abstract|summary|graphical abstract|резюме|аннотация)[\s:.-]*", re.I)


def clean(text):
    """Из JATS, HTML или TeX делает простой текст с пустой строкой между абзацами."""
    if not text:
        return ""
    text = re.sub(r"<(p|/p|sec|/sec)[^>]*>", NL, text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    # остатки TeX из препринтов arXiv: команды, доллары, неразрывные тильды
    text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)
    text = text.replace("$", "").replace("~", " ")
    text = re.sub(r"_\{?([0-9]+)\}?", r"\1", text)          # Fe_2 и Fe_{2} это индексы
    parts = [re.sub(r"\s+", " ", p).strip() for p in text.split(NL)]
    parts = [JUNK.sub("", p) for p in parts if p.strip()]
    # реконструкция абстракта в OpenAlex оставляет пробелы перед знаками препинания
    parts = [re.sub(r"\s+([.,;:!?)])", r"\1", p) for p in parts]
    parts = [re.sub(r"(\()\s+", r"\1", p) for p in parts]
    # так же теряется верхний индекс: «10 465» это 10^465, «cm -3» это cm^-3
    parts = [re.sub(r"(?<![0-9.,-])10 ([0-9]{1,4})(?![0-9])", r"10^\1", p) for p in parts]
    parts = [re.sub(r"\b(cm|nm|m|s|K|Hz|W|mol|L|A|um)\s?[−–-]\s?([0-9])\b", r"\1^-\2", p) for p in parts]
    parts = [re.sub(r"\b(cm|nm|um|m)\s+([23])\b", r"\1^\2", p) for p in parts]
    # и отрывает подстрочные индексы формул: «CsPbBr 3» это CsPbBr3, «La 0.7» это La0.7
    parts = [re.sub(r"\b([A-Z][A-Za-z]{0,5})\s+([0-9]+(?:\.[0-9]+)?)\b", r"\1\2", p) for p in parts]
    return (NL + NL).join(p for p in parts if len(p) > 1)


def site_dois():
    """DOI публикаций, которые стоят на сайте: для остальных абстракт не нужен."""
    text = DATA.read_text(encoding="utf-8")
    return {m.group(1).lower() for m in re.finditer(r'doi: "https://doi\.org/([^"]+)"', text)}


def fetch(url, tries=2, pause=0.0):
    """Запрос с кэшем на диске: повторный сбор не дергает чужие сервисы заново."""
    box = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".json")
    if box.exists():
        return json.loads(box.read_text(encoding="utf-8"))
    if NO_NET:
        return {}
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as f:
                data = json.load(f)
            CACHE.mkdir(exist_ok=True)
            box.write_text(json.dumps(data), encoding="utf-8")
            return data
        except Exception as e:
            if "429" in str(e) and attempt < tries - 1:
                time.sleep(20)
                continue
            return {}
        finally:
            if pause:
                time.sleep(pause)
    return {}


def from_crossref(doi):
    """Абстракт от издателя, разметкой JATS. Есть далеко не у всех журналов."""
    data = fetch("https://api.crossref.org/works/" + doi, pause=0.2)
    return clean((data.get("message") or {}).get("abstract"))


def from_semantic(doi):
    """Semantic Scholar: закрывает заметную часть того, чего нет в OpenAlex и Crossref."""
    data = fetch("https://api.semanticscholar.org/graph/v1/paper/DOI:" + doi + "?fields=abstract",
                 tries=3, pause=1.5)
    return clean(data.get("abstract"))


def from_europepmc(doi):
    """Europe PMC: биомедицинские работы, которых нет в остальных источниках."""
    query = urllib.parse.quote('DOI:"' + doi + '"')
    data = fetch("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=" + query
                 + "&resultType=core&format=json", pause=0.3)
    rows = ((data.get("resultList") or {}).get("result") or [{}])
    return clean(rows[0].get("abstractText"))


def from_twin(doi, db):
    """У препринта той же работы (SSRN, arXiv) абстракт тот же, сеть для этого не нужна."""
    for rec in db["works"]:
        if (rec.get("duplicate_of") or "").lower() == doi and rec.get("abstract"):
            return clean(rec["abstract"])
    return ""


def load_manual():
    """Абстракты, вписанные владельцем руками. Они важнее всего, что отдают сервисы."""
    if not MANUAL.exists():
        return {}
    return {k.lower(): v for k, v in json.loads(MANUAL.read_text(encoding="utf-8")).items() if v.strip()}


def import_md(db):
    """Забирает тексты, вписанные в docs/ABSTRACTS_MISSING.md, в docs/abstracts_manual.json."""
    if not MISSING.exists():
        print("нет файла", MISSING)
        return
    manual = load_manual()
    added = 0
    for chunk in MISSING.read_text(encoding="utf-8").split(NL + "## ")[1:]:
        doi = re.search(r"<!-- doi: ([^\s]+) -->", chunk)
        body = re.search(r"### Абстракт" + NL + "(.*?)$", chunk, re.S)
        if not doi or not body:
            continue
        text = body.group(1).strip()
        text = re.sub(r"^_.*?_$", "", text, flags=re.M).strip()   # подсказка «впишите сюда»
        if len(text) > 120:
            manual[doi.group(1).lower()] = text
            added += 1
    MANUAL.write_text(json.dumps(manual, ensure_ascii=False, indent=1, sort_keys=True),
                      encoding="utf-8", newline=NL)
    print(f"вписано руками: {added}, всего в {MANUAL.name}: {len(manual)}")


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


def write_missing(db, need, found):
    """Список работ без абстракта со ссылками, чтобы владелец добрал их сам."""
    kept = filled_already("Абстракт")
    rows = []
    for rec in db["works"]:
        doi = (rec.get("doi") or "").lower()
        if not doi or doi not in need or doi in found:
            continue
        rows.append(rec)
    rows = [r for r in rows if r["doi"].lower() not in NO_ABSTRACT]
    rows.sort(key=lambda r: (-(r.get("year") or 0), r.get("journal") or ""))
    out = ["# Работы без абстракта", "",
           "Здесь работы, которым абстракт не нашелся ни в OpenAlex, ни в Crossref, Semantic Scholar",
           "и Europe PMC. Откройте ссылку, скопируйте авторский абстракт со страницы статьи и вставьте",
           "его под заголовком «Абстракт», вместо строки-подсказки. Язык оригинала не меняем,",
           "пересказывать и переводить не надо.", "",
           "Потом: `python tools/fetch_abstracts.py --import-md` перенесет тексты",
           "в `docs/abstracts_manual.json`, и они попадут на сайт при следующей сборке.", "",
           f"Всего работ: {len(rows)}", ""]
    for rec in rows:
        out.append("## " + (rec.get("title") or "без названия"))
        out.append("")
        out.append("<!-- doi: " + rec["doi"] + " -->")
        out.append("")
        out.append("%s, %s. %s" % (rec.get("journal") or "издание не указано",
                                   rec.get("year") or "год не указан",
                                   rec.get("authors") or ""))
        out.append("")
        out.append("https://doi.org/" + rec["doi"])
        out.append("")
        out.append("### Абстракт")
        out.append("")
        out.append(kept.get(rec["doi"].lower(), "_впишите сюда_"))
        out.append("")
    MISSING.write_text(NL.join(out).rstrip() + NL, encoding="utf-8", newline=NL)
    print(f"список для ручного добора: {MISSING} ({len(rows)} работ)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="только база и кэш, без новых запросов")
    ap.add_argument("--limit", type=int, default=0, help="сколько работ добирать по сети")
    ap.add_argument("--import-md", dest="import_md", action="store_true",
                    help="забрать тексты из docs/ABSTRACTS_MISSING.md и пересобрать")
    args = ap.parse_args()

    if args.import_md:
        import_md(json.loads(DB.read_text(encoding="utf-8")))

    need = site_dois()
    db = json.loads(DB.read_text(encoding="utf-8"))
    found, missing = {}, []
    for rec in db["works"]:
        doi = (rec.get("doi") or "").lower()
        if not doi or doi not in need or doi in found:
            continue
        text = clean(rec.get("abstract"))
        if len(text) > 120:
            found[doi] = text
        else:
            missing.append(doi)

    manual = load_manual()
    for doi, text in manual.items():
        if doi in need:
            found[doi] = text
            if doi in missing:
                missing.remove(doi)
    print(f"публикаций на сайте с DOI: {len(need)}, абстракт из базы: {len(found) - len(manual)}, "
          f"вписано руками: {len(manual)}, нет: {len(missing)}")

    # у препринта той же работы абстракт тот же, это бесплатно
    by_twin = 0
    for doi in list(missing):
        text = from_twin(doi, db)
        if len(text) > 120:
            found[doi] = text
            missing.remove(doi)
            by_twin += 1
    if by_twin:
        print(f"взято у препринтов той же работы: {by_twin}")

    if args.offline:
        NO_NET.append(True)   # источники опрашиваем, но только по кэшу
    if missing:
        todo = missing[:args.limit] if args.limit else list(missing)
        counts = {"Crossref": 0, "Semantic Scholar": 0, "Europe PMC": 0}
        for i, doi in enumerate(todo, 1):
            for name, source in (("Crossref", from_crossref), ("Semantic Scholar", from_semantic),
                                 ("Europe PMC", from_europepmc)):
                text = source(doi)
                if len(text) > 120:
                    found[doi] = text
                    counts[name] += 1
                    break
            if i % 20 == 0:
                print(f"  {i} из {len(todo)}: " + ", ".join(f"{k} {v}" for k, v in counts.items()), flush=True)
        print("добрано: " + ", ".join(f"{k} {v}" for k, v in counts.items()))

    body = json.dumps(found, ensure_ascii=False, indent=1, sort_keys=True)
    OUT.write_text(
        "/* Авторские абстракты публикаций, ключ — DOI." + NL
        + "   Собирает tools/fetch_abstracts.py из OpenAlex, Crossref, Semantic Scholar и Europe PMC," + NL
        + "   язык оригинала не меняется. Показываются на карточке публикации под авторами." + NL
        + "   Блок раскрывается по клику. */" + NL
        + "window.ABSTRACTS = " + body + ";" + NL, encoding="utf-8", newline=NL)
    left = len(need) - len(found)
    print(f"записано: {OUT} ({len(found)} абстрактов, {OUT.stat().st_size // 1024} КБ), без абстракта: {left}")
    write_missing(db, need, found)


main()
