"""Собирает публикации сотрудников центра из OpenAlex в docs/publications_db.json.

Идентификаторы (ORCID, Scopus ID, Researcher ID, Google Scholar) берутся из книги
«ЦМТ Мост.xlsx» рядом с репозиторием и в репозиторий не попадают: в базу идут только
данные самих статей и русские имена соавторов из центра.

Два способа найти работы человека:
  orcid  — works?filter=author.orcid:...      (доверенный, берем как есть)
  name   — автор OpenAlex с таким именем и аффилиацией ИТМО (требует проверки владельцем)
Совпадения по имени, у которых ORCID автора в OpenAlex противоречит книге, в базу не идут,
а выносятся в отчет.

Запуск: python tools/fetch_publications.py [--xlsx путь] [--report путь]
"""
import argparse
import difflib
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sources import BOOK as XLSX  # книга лежит в data/book, путь ведет общий модуль

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "js" / "data.js"
OUT = ROOT / "docs" / "publications_db.json"
SHEET = "Сотрудники центра"

API = "https://api.openalex.org"
ORCID_API = "https://pub.orcid.org/v3.0"
CROSSREF = "https://api.crossref.org/works"
MAILTO = "bridge@metalab.ifmo.ru"
UA = {"User-Agent": f"cmt-most-site ({MAILTO})"}
ITMO = "I173089394"  # ITMO University в OpenAlex
PAUSE = 0.35

# в книге и в OpenAlex одна и та же фамилия пишется по-разному (Zhestkii / Zhestkij,
# Danny / Danni), поэтому сравниваем имена в огрубленном виде
TRANSLIT = [("yo", "e"), ("kh", "h"), ("zh", "z"), ("sch", "s"), ("sh", "s"),
            ("ch", "c"), ("ts", "c"), ("yu", "u"), ("ya", "a"), ("x", "ks"),
            ("j", "i"), ("y", "i"), ("w", "v")]


CACHE = pathlib.Path(tempfile.gettempdir()) / "cmt_most_openalex"
USE_CACHE = True
SPENT = []  # непустой, когда дневные кредиты OpenAlex кончились


def get(url, tries=4, accept=None):
    """Запрос с кэшем на диске и отступлением при лимите запросов."""
    box = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".json")
    if USE_CACHE and box.exists():
        return json.loads(box.read_text(encoding="utf-8"))
    if SPENT and url.startswith(API):
        raise RuntimeError("дневные кредиты OpenAlex кончились, ждем сброса")
    head = dict(UA, Accept=accept) if accept else UA
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=head), timeout=60) as r:
                data = json.load(r)
            CACHE.mkdir(exist_ok=True)
            box.write_text(json.dumps(data), encoding="utf-8")
            return data
        except Exception as e:
            if attempt == tries - 1 or "404" in str(e):
                if "429" in str(e):
                    SPENT.append(url)  # дальше OpenAlex не дергаем, доживаем на кэше
                raise  # записи просто нет, повторять незачем
            wait = 10 * (attempt + 1) if "429" in str(e) else 3 * (attempt + 1)
            print(f"  повтор через {wait} с ({e})")
            time.sleep(wait)


def pages(path, params):
    """Идет по курсору OpenAlex и отдает все записи."""
    params = dict(params, **{"per-page": 200, "mailto": MAILTO})
    cursor = "*"
    while cursor:
        q = urllib.parse.urlencode(dict(params, cursor=cursor), safe=":,|")
        data = get(f"{API}/{path}?{q}")
        for item in data["results"]:
            yield item
        cursor = data["meta"].get("next_cursor")
        if not data["results"]:
            break
        time.sleep(PAUSE)


def read_people(xlsx):
    """Читает книгу владельца. Возвращает список без почт, телефонов и дат рождения."""
    import openpyxl

    # файл на OneDrive бывает заблокирован (открыт в Excel), работаем с копией;
    # открытую книгу питон скопировать не может, а Copy-Item из PowerShell может
    tmp = pathlib.Path(tempfile.gettempdir()) / "cmt_most_people.xlsx"
    try:
        shutil.copyfile(xlsx, tmp)
    except PermissionError:
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        f'Copy-Item -LiteralPath "{xlsx}" -Destination "{tmp}" -Force'], check=True)
    ws = openpyxl.load_workbook(tmp, data_only=True)[SHEET]
    head = [str(c.value).strip() if c.value else "" for c in ws[1]]
    col = {h: i for i, h in enumerate(head)}
    people = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        full = (row[col["ФИО"]] or "").strip()
        if not full:
            continue
        eng = (row[col["ФИО (eng)"]] or "").strip().split()
        orcid = re.sub(r"[^0-9X-]", "", str(row[col["ORCID"]] or ""))
        born = str(row[col["Дата рождения"]] or "")[:4]
        people.append({
            "full": full,
            "short": short_ru(full),
            "eng": f"{eng[1]} {eng[0]}" if len(eng) > 1 else " ".join(eng),
            "surname_en": eng[0] if eng else "",
            "orcid": orcid if len(orcid) == 19 else "",
            # год рождения в базу не идет, он нужен только чтобы отсеять чужие работы
            "first_year": int(born) + 17 if born.isdigit() else 0,
        })
    os.remove(tmp)
    return people


def short_ru(full):
    """«Зюзин Михаил Валерьевич» -> «Михаил Зюзин» (так люди названы в data.js)."""
    parts = full.split()
    return f"{parts[1]} {parts[0]}" if len(parts) > 1 else full


def site_data():
    """Направления каждого человека и DOI уже опубликованных на сайте работ."""
    text = DATA.read_text(encoding="utf-8")
    dirs = {}
    block = text[text.index("window.DIRECTIONS"):text.index("window.PUBLICATIONS")]
    for chunk in block.split("\n  {")[1:]:
        ident = re.search(r'id:\s*"([^"]+)"', chunk)
        team = re.search(r"people:\s*\[([^\]]*)\]", chunk)
        if not ident or not team:
            continue
        for name in re.findall(r'"([^"]+)"', team.group(1)):
            dirs.setdefault(name, []).append(ident.group(1))
    dois = {d.lower() for d in re.findall(r'doi: "https://doi\.org/([^"]+)"', text)}
    return dirs, dois


def rough(word):
    """Огрубленная латиница: Zhestkii, Zhestkij и Zhestkiy сходятся в одно слово."""
    word = re.sub(r"[^a-z]", "", word.lower())
    for a, b in TRANSLIT:
        word = word.replace(a, b)
    return re.sub(r"(.)\1+", r"\1", word)


def name_fits(person, display):
    """Тот же человек, что в книге: сходятся и имя, и фамилия (с учетом транслитерации)."""
    parts = display.split()
    if len(parts) < 2:
        return False
    book = person["eng"].split()
    return rough(parts[0]) == rough(book[0]) and rough(parts[-1]) == rough(book[-1])


def name_close(person, other):
    """Мягкая сверка имени: ловит чужого человека, но терпит Oleksii вместо Aleksei."""
    cyr = bool(re.search(r"[а-яА-Я]", other))
    def words(s):
        got = re.findall(r"[а-яa-z]+", s.lower())
        return [w for w in (got if cyr else [rough(w) for w in got]) if w]
    theirs, mine = words(other), words(person["full"] if cyr else person["eng"])
    if not theirs or not mine:
        return True  # в профиле имя скрыто, сверять нечего
    # порядок слов в профилях разный, поэтому каждое слово меряем с лучшим из наших
    best = [max(difflib.SequenceMatcher(None, w, m).ratio() for m in mine) for w in theirs]
    return sum(best) / len(best) >= 0.7


def orcid_owner(orcid):
    """Чье имя стоит в профиле ORCID (проверяем, что в книге не опечатка)."""
    person = get(f"{ORCID_API}/{orcid}/person", accept="application/json")
    name = person.get("name") or {}
    given = ((name.get("given-names") or {}) or {}).get("value") or ""
    family = ((name.get("family-name") or {}) or {}).get("value") or ""
    return f"{given} {family}".strip()


def find_authors(person):
    """Авторы OpenAlex для человека: по ORCID и по фамилии среди авторов ИТМО."""
    found, seen = [], set()
    if person["orcid"]:
        for a in pages("authors", {"filter": f"orcid:{person['orcid']}"}):
            seen.add(a["id"])
            found.append((a, "orcid", ""))
    if not person["surname_en"]:
        return found
    # поиск OpenAlex ищет слово целиком, поэтому пробуем и другие написания фамилии
    for q in surname_spellings(person["surname_en"]):
        # фамилию не кодируем руками: urlencode внутри pages() сделает это сам
        hits = 0
        for a in pages("authors", {"filter": f"display_name.search:{q},affiliations.institution.id:{ITMO}"}):
            if a["id"] in seen or not name_fits(person, a["display_name"]):
                continue  # однофамильцы ИТМО, их в базу не берем
            seen.add(a["id"])
            hits += 1
            their = (a["ids"].get("orcid") or "").rsplit("/", 1)[-1]
            if person["orcid"] and their and their != person["orcid"]:
                found.append((a, "conflict", f"ORCID в OpenAlex {their} не совпадает с книгой"))
            else:
                found.append((a, "name", f"совпадение по имени ({q}) и аффилиации ИТМО"))
        if hits:
            break
    return found


def surname_spellings(surname):
    """Написания фамилии, по которым стоит поискать автора: Zhestkii, Zhestkij, Zhestkiy, Zhestky."""
    out = [surname]
    stem = re.sub(r"(ii|ij|iy|y|i)$", "", surname)
    if stem != surname:
        out += [stem + end for end in ("ii", "ij", "iy", "y", "i")]
    for a, b in (("kh", "h"), ("ia", "ya"), ("ya", "ia"), ("iu", "yu"), ("yu", "iu")):
        if a in surname.lower():
            out.append(re.sub(a, b, surname, flags=re.I))
    seen, uniq = set(), []
    for s in out:
        if s.lower() not in seen:
            seen.add(s.lower())
            uniq.append(s)
    return uniq


TYPES = {"journal-article": "article", "proceedings-article": "conference-paper",
         "posted-content": "preprint", "book-section": "book-chapter"}

# работы полных тезок, проверены владельцем вручную: в базу не берем ни при каком сборе.
# ключ - DOI, а если его нет, то название в огрубленном виде (см. flat)
STRANGERS = {
    "10.1063/1.3659880": "пылевая плазма, V. V. Yaroshenko из Института Макса Планка",
    "10.1016/j.icarus.2015.04.028": "Энцелад, тот же однофамилец",
    "10.1134/s0006350919010056": "SASCUBE, рентгеновское рассеяние, не наш Ярошенко (проверено владельцем)",
    "modellingofcassinichargingandwakeformationinsaturnsmagnetosphere":
        "Кассини, тот же однофамилец, работа без DOI",
    "10.15593/2411-4367/2017.04.06":
        "оптоволоконные сенсоры, в профиле Артема Ларина работы нет, тема чужая (проверено владельцем)",
    "10.1134/s0021364022200012":
        "спектр оптического фонона, среди авторов нет никого из центра (проверено владельцем)",
    "10.24160/1993-6982-2023-6-77-87":
        "подогреватели воды на ТЭЦ, Pavel Kustov из другой области (ORCID привязан ошибочно)",
}

# работы, которых нет ни в OpenAlex, ни в профилях ORCID: нашлись при сверке с Google Scholar.
# DOI -> кто из центра в соавторах (проверено владельцем, повторной проверки не требуют)
EXTRA = {
    "10.1109/iclo69056.2026.11624674": ["Елена Герасимова", "Лидия Михайлова", "Михаил Зюзин"],
    # Николай Жесткий: в OpenAlex его ORCID пустой, а имя пишется то Zhestkij, то Zhestkii
    "10.1002/adom.202300881": ["Николай Жесткий"],
    "10.1016/j.photonics.2021.100990": ["Николай Жесткий"],
    "10.1038/s43246-024-00573-6": ["Николай Жесткий"],
    "10.1002/adfm.202311235": ["Николай Жесткий"],
    "10.1021/jacs.6c00409": ["Николай Жесткий"],
    "10.1021/acsami.3c10193": ["Николай Жесткий"],
    "10.3390/cryst12060846": ["Николай Жесткий"],
    "10.1016/j.photonics.2023.101145": ["Николай Жесткий"],
    "10.1016/j.photonics.2023.101198": ["Николай Жесткий"],
    "10.15826/chimtech.2021.8.4.11": ["Николай Жесткий"],
    "10.1002/lpor.202401912": ["Николай Жесткий"],
    "10.1002/lpor.202501152": ["Николай Жесткий"],
    "10.1021/acsanm.5c04932": ["Николай Жесткий"],
    "10.1021/acs.jpcc.4c04885": ["Николай Жесткий"],
    "10.1039/d5qm00166h": ["Николай Жесткий"],
    "10.1109/iclo69056.2026.11624504": ["Николай Жесткий"],
    "10.1117/12.3100337": ["Николай Жесткий"],
    "10.1117/12.3105976": ["Николай Жесткий"],
    "10.1117/12.3022176": ["Николай Жесткий"],
    "10.1117/12.2691151": ["Николай Жесткий"],
    # Артем Ларин: работы из его профиля Scholar, которых не было в базе или где его не было в авторах
    "10.29026/oea.2025.250110": ["Артем Ларин"],
    "10.1109/iclo69056.2026.11624504": ["Артем Ларин"],
    "10.17586/2220-8054-2025-16-6-785-790": ["Артем Ларин"],
    "10.17586/1023-5086-2026-93-03-33-39": ["Артем Ларин", "Дмитрий Зуев"],
    # Эдуард Агеев: из его профиля Scholar
    "10.1109/iclo69056.2026.11625116": ["Эдуард Агеев", "Екатерина Понкратова",
                                        "Александр Лошкарев", "Мартин Сандомирский"],
    # Михаил Зюзин: из его профиля Scholar
    "10.1109/iclo69056.2026.11624899": ["Михаил Зюзин", "Лидия Михайлова"],
    "10.1109/iclo69056.2026.11624559": ["Михаил Зюзин", "Иван Резник", "Арина Чередникова",
                                        "Сабина Бикметова"],
    "10.1109/iclo69056.2026.11625054": ["Михаил Зюзин", "Лидия Михайлова", "Мария Тимофеева",
                                        "Арина Чередникова"],
    "10.1134/s1990750826600287": ["Михаил Зюзин"],
}

# работам без DOI соавторов из центра дописываем по названию (тоже по профилям Scholar)
EXTRA_TITLES = {
    "Study of multipotent mesenchymal stromal cells as a cellular delivery system "
    "for antitumor drugs and their remote control activation": ["Михаил Зюзин"],
    "Polymeric micro-and nano-carriers as a universal platform for delivery "
    "of biologically active substances to therapeutically cell populations": ["Михаил Зюзин"],
}


def abstract_of(work):
    index = work.get("abstract_inverted_index")
    if not index:
        return ""
    words = {}
    for word, spots in index.items():
        for spot in spots:
            words[spot] = word
    return " ".join(words[i] for i in sorted(words))


def work_record(work):
    place = work.get("primary_location") or {}
    source = place.get("source") or {}
    biblio = work.get("biblio") or {}
    oa = work.get("open_access") or {}
    doi = (work.get("doi") or "").replace("https://doi.org/", "")
    return {
        "doi": doi,
        "openalex": work["id"].rsplit("/", 1)[-1],
        "title": work.get("title") or "",
        "journal": source.get("display_name") or "",
        "publisher": source.get("host_organization_name") or "",
        "date": work.get("publication_date") or "",
        "year": work.get("publication_year"),
        "type": TYPES.get(work.get("type") or "", work.get("type") or ""),
        "itmo": any(i["id"].endswith(ITMO) for a in work.get("authorships", [])
                    for i in a.get("institutions", [])),
        "volume": biblio.get("volume"),
        "issue": biblio.get("issue"),
        "pages": "-".join(p for p in [biblio.get("first_page"), biblio.get("last_page")] if p) or None,
        "authors": ", ".join(a.get("raw_author_name") or "" for a in work.get("authorships", [])),
        "authors_count": len(work.get("authorships", [])),
        "cited_by": work.get("cited_by_count", 0),
        "open_access": bool(oa.get("is_oa")),
        "oa_url": oa.get("oa_url") or "",
        "language": work.get("language") or "",
        "retracted": bool(work.get("is_retracted")),
        "keywords_en": [k.get("display_name") for k in (work.get("keywords") or [])],
        "topics": [t.get("display_name") for t in (work.get("topics") or [])[:3]],
        "abstract": abstract_of(work),
        "center_authors": [],
        "match": {},
        "needs_check": False,
        "direction_candidates": [],
        "on_site": False,
    }


def flat(title):
    """Название без регистра и знаков, чтобы ловить одну работу в разных источниках."""
    return re.sub(r"[^0-9a-zа-я]+", "", (title or "").lower())


# что считаем главной версией работы, когда название совпало
RANK = ["article", "conference-paper", "book-chapter", "preprint", "other"]

# русский журнал и его переводная английская версия: одна и та же статья выходит в обоих
TRANSLATED = [
    ("письма в журнал технической физики", "technical physics letters"),
    ("письма в журнал экспериментальной", "jetp letters"),
    ("письма в журнал экспериментальной", "journal of experimental and theoretical"),
    ("физика и техника полупроводников", "semiconductors"),
    ("неорганические материалы", "inorganic materials"),
    ("журнал технической физики", "technical physics"),
    ("оптика и спектроскопия", "optics and spectroscopy"),
]


def mark_translations(works):
    """Помечает русский оригинал, если в базе уже есть его английский перевод."""
    doubles = 0
    latin = [r for r in works.values() if r["title"] and not re.search(r"[а-яА-Я]", r["title"])]
    for rec in works.values():
        if rec.get("duplicate_of") or not re.search(r"[а-яА-Я]", rec["title"] or ""):
            continue
        ru = rec["journal"].lower()
        names = [en for rus, en in TRANSLATED if rus in ru]
        for other in latin:
            if (names and any(en in other["journal"].lower() for en in names)
                    and other["year"] == rec["year"] and other["authors_count"] == rec["authors_count"] > 2):
                if rec.get("on_site") and not other.get("on_site"):
                    break  # на сайте стоит русская версия с ручной разметкой, ее и оставляем
                rec["duplicate_of"] = other["doi"] or other["openalex"]
                doubles += 1
                print("перевод той же статьи:", rec["title"][:55], "->", other["journal"][:35])
                break
    return doubles


def mark_duplicates(works):
    """Помечает препринты и вторые DOI той же работы, чтобы они не шли на сайт дважды."""
    groups = {}
    for key, rec in works.items():
        if rec["title"]:
            groups.setdefault(flat(rec["title"]), []).append((key, rec))
    doubles = 0
    for same in groups.values():
        for _, rec in same:
            rec["duplicate_of"] = ""
        if len(same) < 2:
            continue
        # работа, которая уже стоит на сайте, остается главной: у нее ручная разметка
        rank = lambda kr: (not kr[1].get("on_site"),
                           RANK.index(kr[1]["type"]) if kr[1]["type"] in RANK else len(RANK),
                           -kr[1]["cited_by"], not kr[1]["doi"])
        main = sorted(same, key=rank)[0]
        for key, rec in same:
            if key == main[0]:
                continue
            rec["duplicate_of"] = main[1]["doi"] or main[0]
            doubles += 1
            # соавторов центра сводим к главной записи, чтобы никто не потерялся
            for name, how in rec["match"].items():
                if name not in main[1]["center_authors"]:
                    main[1]["center_authors"].append(name)
                main[1]["match"].setdefault(name, how)
    return doubles


def key_of(doi, fallback):
    """Ключ записи: DOI, а если его нет, то идентификатор работы в источнике."""
    return (f"https://doi.org/{doi}" if doi else fallback).lower()


def load_db(path):
    """Прошлая выгрузка, чтобы неудачный запрос к источнику не обнулял базу."""
    path = pathlib.Path(path)
    if not path.exists():
        return {}
    old = json.loads(path.read_text(encoding="utf-8"))
    db = {}
    for r in old.get("works", []):
        if isinstance(r.get("match"), list):  # формат первых выгрузок
            r["match"] = dict(zip(r["center_authors"], r["match"]))
        r["doi"] = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", (r["doi"] or "").lower())
        key = key_of(r["doi"], r.get("openalex") or f"title:{flat(r['title'])}")
        if key in db:  # разные ключи прошлых выгрузок могли указывать на одну работу
            db[key]["center_authors"] = sorted(set(db[key]["center_authors"] + r["center_authors"]))
            db[key]["match"].update(r["match"])
            continue
        db[key] = r
    return db


def orcid_works(orcid):
    """Работы из профиля ORCID: заголовок, журнал, дата, DOI."""
    data = get(f"{ORCID_API}/{orcid}/works", accept="application/json")
    for group in data.get("group", []):
        summary = group["work-summary"][0]
        ids = {i["external-id-type"]: i["external-id-value"]
               for i in (group.get("external-ids") or {}).get("external-id", [])}
        date = summary.get("publication-date") or {}
        parts = [(date.get(k) or {}).get("value") for k in ("year", "month", "day")]
        yield {
            # в ORCID DOI бывает записан ссылкой или с приставкой doi:
            "doi": re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", (ids.get("doi") or "").strip().lower()),
            "title": ((summary.get("title") or {}).get("title") or {}).get("value") or "",
            "journal": (summary.get("journal-title") or {}).get("value") or "",
            "type": (summary.get("type") or "").lower().replace("_", "-"),
            "date": "-".join(p.zfill(2) if i else p for i, p in enumerate(parts) if p),
            "year": int(parts[0]) if parts[0] else None,
            "put_code": str(summary.get("put-code") or ""),
        }


def plain(text):
    """Убирает разметку и лишние пробелы: в Crossref в названиях бывает <sub>, <i> и переносы."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", text or "")).strip()


def crossref_record(doi):
    """Карточка работы из Crossref (когда работы нет в OpenAlex)."""
    m = get(f"{CROSSREF}/{urllib.parse.quote(doi)}")["message"]
    date = (m.get("published-print") or m.get("published-online") or m.get("issued") or {}).get("date-parts", [[None]])[0]
    authors = [" ".join(p for p in [a.get("given"), a.get("family")] if p) or a.get("name", "")
               for a in m.get("author", [])]
    return {
        "doi": doi,
        "openalex": "",
        "title": plain((m.get("title") or [""])[0]),
        "journal": plain((m.get("container-title") or [""])[0]),
        "publisher": m.get("publisher") or "",
        "date": "-".join(str(p).zfill(2) if i else str(p) for i, p in enumerate(date) if p),
        "year": date[0] if date else None,
        "type": TYPES.get(m.get("type") or "", m.get("type") or ""),
        "itmo": "itmo" in json.dumps(m.get("author", []), ensure_ascii=False).lower(),
        "volume": m.get("volume"),
        "issue": m.get("issue"),
        "pages": m.get("page") or m.get("article-number"),
        "authors": ", ".join(authors),
        "authors_count": len(authors),
        "cited_by": m.get("is-referenced-by-count", 0),
        "open_access": False,
        "oa_url": "",
        "language": m.get("language") or "",
        "retracted": False,
        "keywords_en": m.get("subject") or [],
        "topics": [],
        "abstract": plain(m.get("abstract")),
        "center_authors": [],
        "match": {},
        "needs_check": False,
        "direction_candidates": [],
        "on_site": False,
        "source": "crossref",
    }


def orcid_record(item):
    """Карточка из профиля ORCID, когда работы нет ни в OpenAlex, ни в Crossref."""
    rec = dict.fromkeys(["publisher", "volume", "issue", "pages", "language", "oa_url", "abstract"], "")
    rec.update({
        "doi": item["doi"], "openalex": "", "title": item["title"], "journal": item["journal"],
        "date": item["date"], "year": item["year"], "type": TYPES.get(item["type"], item["type"]),
        "itmo": False,
        "authors": "", "authors_count": 0, "cited_by": 0, "open_access": False, "retracted": False,
        "keywords_en": [], "topics": [], "center_authors": [], "match": {}, "needs_check": True,
        "direction_candidates": [], "on_site": False, "source": "orcid",
    })
    return rec


def add_person(rec, person, how, row):
    if person["short"] not in rec["center_authors"]:
        rec["center_authors"].append(person["short"])
        row["works"] += 1
    if rec["match"].get(person["short"]) != "orcid":
        rec["match"][person["short"]] = how


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", default=str(XLSX))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--report", default="")
    ap.add_argument("--no-openalex", action="store_true", help="только профили ORCID и Crossref")
    args = ap.parse_args()

    people = read_people(pathlib.Path(args.xlsx))
    dirs, site_dois = site_data()
    works, report = load_db(args.out), []

    for person in people:
        owner = ""
        if person["orcid"]:
            try:
                owner = orcid_owner(person["orcid"])
            except Exception as e:
                print(f"  профиль ORCID не открылся у {person['short']} ({e})")
            if owner and not name_close(person, owner):
                print(f"  ORCID из книги принадлежит другому человеку: {person['short']} -> {owner}")
                person["orcid"] = ""
        try:
            authors = [] if args.no_openalex else find_authors(person)
        except Exception as e:  # кончились кредиты OpenAlex: работаем тем, что есть
            print(f"  OpenAlex недоступен для {person['short']} ({e})")
            authors = []
        taken = [a for a in authors if a[1] in ("orcid", "name")]
        row = {
            "name": person["short"],
            "method": taken[0][1] if taken else "нет",
            "authors": [],
            "skipped": [{"name": a[0]["display_name"], "works": a[0]["works_count"], "why": a[2]}
                        for a in authors if a[1] == "conflict"],
            "works": 0,
            "from_orcid": 0,
            "orcid_owner": owner if owner and not person["orcid"] else "",
        }
        for author, how, why in taken:
            ident = author["id"].rsplit("/", 1)[-1]
            row["authors"].append({"name": author["display_name"], "works": author["works_count"], "why": why})
            try:
                found = list(pages("works", {"filter": f"author.id:{ident}"}))
            except Exception as e:
                print(f"  OpenAlex недоступен для {person['short']} ({e})")
                continue
            for work in found:
                if work.get("is_paratext"):
                    continue
                key = (work.get("doi") or work["id"]).lower()
                fresh = dict(work_record(work), source="openalex")
                if key in works:  # обновляем библиографию, разметку работы не трогаем
                    for field in ("center_authors", "match", "needs_check", "on_site",
                                  "direction_candidates", "direction_votes"):
                        fresh.pop(field, None)
                    works[key].update(fresh)
                else:
                    works[key] = fresh
                add_person(works[key], person, how, row)

        # профиль ORCID: то, что человек ведет сам, в OpenAlex попадает не всегда
        if person["orcid"]:
            for item in orcid_works(person["orcid"]):
                # без DOI ключом служит название, иначе одна работа придет от каждого соавтора
                key = key_of(item["doi"], f"title:{flat(item['title'])}")
                if key not in works:
                    try:
                        works[key] = crossref_record(item["doi"]) if item["doi"] else orcid_record(item)
                    except Exception as e:
                        print(f"  нет данных Crossref по {item['doi']} ({e})")
                        works[key] = orcid_record(item)
                    row["from_orcid"] += 1
                add_person(works[key], person, "orcid", row)
                time.sleep(PAUSE)

        if row["method"] == "нет" and row["from_orcid"]:
            row["method"] = "профиль ORCID"
        report.append(row)
        print(f"{row['works']:5d}  {person['short']}  [{row['method']}]"
              + (f", из профиля ORCID добавлено {row['from_orcid']}" if row["from_orcid"] else ""))

    # работы, добавленные руками после сверки с Google Scholar
    for doi, names in EXTRA.items():
        key = key_of(doi, "")
        if key not in works:
            try:
                works[key] = dict(crossref_record(doi), source="сверка с Scholar")
                print("добавлена руками:", works[key]["title"][:60])
            except Exception as e:
                print("нет данных Crossref по добавленной работе", doi, e)
                continue
        for name in names:
            if name not in works[key]["center_authors"]:
                works[key]["center_authors"].append(name)
            works[key]["match"][name] = "проверено"

    want = {flat(t): names for t, names in EXTRA_TITLES.items()}
    for rec in works.values():
        for name in want.get(flat(rec["title"]), []):
            if name not in rec["center_authors"]:
                rec["center_authors"].append(name)
            rec["match"][name] = "проверено"

    # статьи, которые уже стоят на сайте, но не нашлись ни по ORCID, ни по имени
    for doi in site_dois:
        if key_of(doi, "") in works:
            continue
        try:
            works[key_of(doi, "")] = dict(crossref_record(doi), source="сайт")
            print("добрано с сайта:", doi)
        except Exception as e:
            print("нет данных Crossref по публикации сайта", doi, e)

    for key in [k for k, r in works.items()
                if r["doi"].lower() in STRANGERS or flat(r["title"]) in STRANGERS]:
        print("работа тезки, не берем:", works[key]["title"][:60])
        del works[key]

    # человека, найденного только по имени, оставляем в работе, если она вообще связана
    # с ИТМО: иначе к нему прилипают статьи полного тезки из другого института
    stranger = 0
    for rec in works.values():
        # itmo = None означает, что аффилиацию мы еще не смотрели, такие записи не трогаем
        if rec["itmo"] is False and len(rec["center_authors"]) < 2:
            for name, how in list(rec["match"].items()):
                if how == "name":
                    rec["center_authors"].remove(name)
                    rec["match"].pop(name)
                    stranger += 1
    if stranger:
        print(f"\nснято привязок по имени без связи с ИТМО: {stranger}")

    # в OpenAlex под одним именем бывают склеены разные люди: работу, вышедшую до того,
    # как человек мог начать печататься, ему не приписываем
    born = {p["short"]: p["first_year"] for p in people}
    early = 0
    for rec in works.values():
        for name in list(rec["center_authors"]):
            if (rec["year"] or 0) and born.get(name, 0) and rec["year"] < born[name]:
                rec["center_authors"].remove(name)
                rec["match"].pop(name, None)
                early += 1
    for key in [k for k, r in works.items() if not r["center_authors"] and not r["on_site"]
                and r["doi"].lower() not in site_dois]:
        del works[key]
    if early:
        print(f"\nснято привязок по году: {early}")

    # отметку «стоит на сайте» ставим до поиска дублей: она решает, какая версия главная
    for rec in works.values():
        rec["on_site"] = rec["doi"].lower() in site_dois

    doubles = mark_duplicates(works)
    doubles += mark_translations(works)

    for rec in works.values():
        rec.setdefault("source", "openalex")
        rec.setdefault("itmo", None)  # None = аффилиацию еще не смотрели
        rec["type"] = TYPES.get(rec["type"], rec["type"])
        rec["title"], rec["journal"] = plain(rec["title"]), plain(rec["journal"])
        rec["on_site"] = rec["doi"].lower() in site_dois
        trusted = {"orcid", "проверено"}
        rec["needs_check"] = bool(rec["match"]) and not trusted & set(rec["match"].values())
        # направление тем вероятнее, чем больше авторов центра из его команды
        votes = {}
        for name in rec["center_authors"]:
            for d in dirs.get(name, []):
                votes[d] = votes.get(d, 0) + 1
        rec["direction_candidates"] = [d for d, _ in sorted(votes.items(), key=lambda kv: -kv[1])]
        rec["direction_votes"] = votes

    rows = sorted(works.values(), key=lambda r: (r["date"] or "", r["title"]), reverse=True)
    db = {
        "generated": time.strftime("%Y-%m-%d"),
        "source": "OpenAlex, профили ORCID, Crossref",
        "note": "Черновая база. Записи с match «name» проверяет владелец, поля tags и desc заполняются вручную.",
        "people_total": len(people),
        "works_total": len(rows),
        "duplicates": doubles,
        "unique_total": len(rows) - doubles,
        "works": rows,
    }
    pathlib.Path(args.out).write_text(json.dumps(db, ensure_ascii=False, indent=1) + "\n",
                                      encoding="utf-8", newline="\n")
    if args.report:
        pathlib.Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n",
                                             encoding="utf-8", newline="\n")
    on_site = sum(1 for r in rows if r["on_site"])
    print(f"\nработ: {len(rows)}, из них дублей: {doubles}, уже на сайте: {on_site}, "
          f"новых без дублей: {len(rows) - doubles - on_site}")
    print("записано:", args.out)


# запускается как скрипт, а из publications_to_data.py импортируется список STRANGERS
if __name__ == "__main__":
    main()
