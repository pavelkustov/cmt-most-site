"""Проставляет публикациям в data.js квартиль журнала и число цитирований.

Квартиль берется из выгрузки SJR (Scimago): CSV-файлы вида «scimagojr 2025.csv» рядом
с репозиторием. Сам сайт их не использует, в репозиторий они не кладутся: скрипт
сохраняет разобранную карту «журнал -> квартиль» в docs/journal_quartiles.json,
дальше хватает ее одной. Берется лучший квартиль журнала (SJR Best Quartile) за самый
свежий год, где журнал есть в рейтинге.

Цитирования берутся из docs/publications_db.json (поле cited_by, источник OpenAlex).

Сборники конференций и препринты пропускаются: квартиля у них нет.
У русских журналов SJR тоже нет, они перечислены в MANUAL, значения владелец проставляет
руками (или оставляет пустыми, тогда значка на карточке не будет).

Запуск: python tools/enrich_publications.py [--dry] [--csv-dir ПАПКА]
"""
import argparse
import csv
import gzip
import html
import io
import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "js" / "data.js"
DB = ROOT / "docs" / "publications_db.json"
MAP = ROOT / "docs" / "journal_quartiles.json"
SJR = ROOT / "data" / "sjr"   # оригиналы выгрузок SJR, сюда же кладутся новые

# русские журналы без английской версии: в рейтинге SJR их нет вовсе, квартиля не будет.
# Если он у журнала появится, значение вписывается сюда руками
MANUAL = {
    "Современные наукоемкие технологии (Modern High Technologies)": "",
    "Известия вузов Пищевая технология": "",
    "NAUCHNOE PRIBOROSTROENIE": "",
    "Applied photonics": "",
    "Oil and Gas technologies": "",
    "Ophthalmology in Russia": "",
    "Physics of Complex Systems": "",
}

# издания, которые в SJR названы иначе, чем в метаданных работы
ALIAS = {
    "Journal of Experimental and Theoretical Physics Letters": "JETP Letters",
    # русские журналы: квартиль берется у их английской переводной версии
    "Письма в журнал технической физики": "Technical Physics Letters",
    "Оптический журнал": "Journal of Optical Technology",
    "Оптика и спектроскопия": "Optics and Spectroscopy",
    "Современные технологии в медицине": "Sovremennye Tehnologii v Medicine",
    "Izvestiya vysshikh uchebnykh zavedenii Fizika": "Russian Physics Journal",
    "中国科学通报：英文版": "Science Bulletin",
    "Diffusion and defect data, solid state data. Part B, Solid state phenomena/Solid state phenomena": "Solid State Phenomena",
    "Materials Science and Engineering C": "Materials Science and Engineering: C",
    "Angewandte Chemie": "Angewandte Chemie - International Edition",
}

# сборники конференций, препринты и работы без издания: квартиля не бывает
SKIP_RE = re.compile(
    r"^\d{4}\b|proceedings|conference|congress|symposium|web of conferences|arxiv|ssrn|"
    r"chemrxiv|research square|preprints\.org|figshare|fraunhofer|iclo|eu pvsec|"
    r"ieee nano|metamaterials \d{4}|publication database|doaj|japan society of applied physics|"
    r"non-equilibrium phase transformations|nonlinear optics and its applications|"
    r"\b(i{1,3}|iv|vi{0,3}|ix|x{1,2})$",
    re.I)

SYN = {"reviews": "review", "letters": "letter", "materials": "material", "applications": "application",
       "sciences": "science", "technologies": "technology", "journal": "j", "physics": "phys",
       "physical": "phys", "chemistry": "chem", "chemical": "chem", "proceedings": "proceeding"}


def key(title):
    """Огрубленное название: регистр, амперсанд, служебные слова и окончания не мешают."""
    s = html.unescape(title or "").lower()
    s = unicodedata.normalize("NFKD", s).replace("&", " and ")
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"\b(the|of|for|in|on|a|an|and)\b", " ", s)
    s = re.sub(r"[^a-z0-9а-я ]+", " ", s)
    return " ".join(SYN.get(w, w) for w in s.split())


def keys_for(title):
    out = {key(title)}
    if ":" in title:
        out.add(key(title.split(":")[0]))
    return {k for k in out if k}


def open_sjr(path):
    """Выгрузка читается как есть или сжатой, чтобы оригиналы можно было хранить в gzip."""
    if path.suffix == ".gz":
        return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8")
    return io.open(path, encoding="utf-8")


def read_sjr(folder):
    """Карта «огрубленное название -> квартиль» из выгрузок SJR, свежий год важнее."""
    files = sorted(list(folder.glob("scimagojr *.csv")) + list(folder.glob("scimagojr *.csv.gz")),
                   key=lambda p: p.name, reverse=True)
    index, years = {}, []
    for path in files:
        year = re.search(r"(\d{4})", path.name).group(1)
        if year in years:
            continue
        years.append(year)
        for row in csv.DictReader(open_sjr(path), delimiter=";"):
            if (row.get("Type") or "").strip() not in ("journal", "book series"):
                continue
            q = (row.get("SJR Best Quartile") or "").strip()
            if q not in ("Q1", "Q2", "Q3", "Q4"):
                continue
            for k in keys_for(row["Title"]):
                if k not in index:  # первый год в порядке убывания и есть самый свежий
                    index[k] = {"quartile": q, "year": year, "title": row["Title"]}
    return index, years


def blocks(text):
    start = text.index("window.PUBLICATIONS = [") + len("window.PUBLICATIONS = [")
    end = text.index("\n];", start)
    return text[:start], re.findall(r"\n  \{.*?\n  \},", text[start:end], re.S), text[end:]


def put(block, name, value):
    """Дописывает или меняет поле в первой строке записи (там, где дата и журнал)."""
    if re.search(rf"\b{name}: ", block):
        return re.sub(rf"\b{name}: (\[[^\]]*\]|\"[^\"]*\"|\d+)", f"{name}: {value}", block, count=1)
    return block.replace("direction:", f"{name}: {value}, direction:", 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="только отчет, файл не трогать")
    ap.add_argument("--csv-dir", default=str(SJR), help="папка с выгрузками «scimagojr ГОД.csv»")
    args = ap.parse_args()

    stored = json.loads(MAP.read_text(encoding="utf-8")) if MAP.exists() else {}
    index, years = read_sjr(pathlib.Path(args.csv_dir))
    print(f"выгрузки SJR: {', '.join(years) if years else 'не найдены, берем docs/journal_quartiles.json'}")

    db = json.loads(DB.read_text(encoding="utf-8"))
    cited = {(r["doi"] or "").lower(): r.get("cited_by") or 0 for r in db["works"] if r.get("doi")}

    text = DATA.read_text(encoding="utf-8")
    head, old, tail = blocks(text)
    fresh, unknown, done, cites = dict(stored), {}, 0, 0
    result = []
    for block in old:
        journal = (re.search(r'journal: "([^"]*)"', block) or [None, ""])[1]
        doi = re.search(r'doi: "https://doi\.org/([^"]+)"', block)
        if doi and doi.group(1).lower() in cited:
            block = put(block, "cited", cited[doi.group(1).lower()])
            cites += 1
        if journal and not SKIP_RE.search(journal):
            q = MANUAL.get(journal)
            if q is None:
                hit = None
                for k in keys_for(ALIAS.get(journal, journal)):
                    hit = index.get(k) or stored.get(journal)
                    if hit:
                        break
                if hit:
                    q = hit["quartile"] if isinstance(hit, dict) else hit
                    fresh[journal] = hit if isinstance(hit, dict) else {"quartile": hit}
                else:
                    unknown[journal] = unknown.get(journal, 0) + 1
            if q:
                block = put(block, "quartile", json.dumps(q))
                done += 1
        result.append(block)

    print(f"публикаций: {len(old)}, проставлен квартиль: {done}, цитирования: {cites}")
    if unknown:
        print("журнал не найден в SJR (%d):" % len(unknown))
        for name, n in sorted(unknown.items(), key=lambda kv: -kv[1]):
            print(f"   {n:>3}  {name}")
    empty = [name for name, q in MANUAL.items() if not q]
    if empty:
        print("ждут квартиля от владельца (%d): %s" % (len(empty), "; ".join(empty)))
    if args.dry:
        return
    DATA.write_text(head + "".join(result) + tail, encoding="utf-8", newline="\n")
    MAP.write_text(json.dumps(fresh, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    print("записано:", DATA, "и", MAP)


main()
