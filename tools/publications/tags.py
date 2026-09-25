"""Чистит ключевые теги публикаций сайта и добирает их там, где тегов нет.

Теги новых работ приходят из OpenAlex, а он размечает их концептами, у которых в скобках
стоит дисциплина, в которой слово понимается: «Substrate (aquarium)», «Absorption (acoustics)»,
«Work (physics)». Скобки убираем, а слова, которые без скобок ничего не значат («Work»,
«Range», «Process»), выбрасываем совсем. Широкие названия областей («Materials science»,
«Chemistry») не выбрасываем, а сдвигаем в конец списка: на карточке видна первая строка,
и в ней должны стоять слова про саму работу.

Теги стоят на языке статьи: у русской работы русские, у английской английские. Если язык
не тот, английские берутся из OpenAlex, а русские вписывает владелец.

Работам без тегов теги добираются из OpenAlex по DOI. Если и там пусто, работа попадает
в content/edit/TAGS_MISSING.md: владелец вписывает ключевые слова со страницы статьи, а
`--import-md` переносит их в content/manual/tags.json, откуда они и идут на сайт.

Запуск: python tools/publications/tags.py [--dry] [--offline] [--import-md]
"""
import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib.paths import EDIT, MANUAL_TAGS as MANUAL_FILE, PUBLICATIONS, PUBLICATIONS_DB as DB
from lib.store import load, rel, save, write
from lib.web import openalex

MISSING = EDIT / "TAGS_MISSING.md"   # список работ без тегов, владелец вписывает слова
NL = chr(10)

# ключевые слова, выписанные со страницы издателя: у этих работ в OpenAlex тегов нет
# или он подобрал их к чужой работе (21.09.2026)
MANUAL = {
    # opticjourn.ru/ru/abstract/2026-93-3-33-39, раздел «Ключевые слова»
    "10.17586/1023-5086-2026-93-03-33-39": [
        "генерация второй гармоники", "кремний", "поверхностные ловушки",
        "эффект памяти", "гистерезис"],
    # joam.inoe.ro/articles/laser-induced-phase-structure-changes-psc-in-glass-like-materials/
    "Laser-induced phase-structure changes (PSC) in glass-like materials": [
        "Phase structure changes", "Laser induced changes"],
    # opticjourn.ru, статья на русском, ключевые слова авторские
    "10.26297/0579-3009.2026.1.3": [
        "липосомы", "промышленные фосфатиды", "соевый лецитин", "подсолнечный лецитин",
        "липидный состав", "фосфолипиды", "ресвератрол", "инкапсуляция"],
    # cttjournal.com, раздел KEYWORDS на странице статьи
    "Study of multipotent mesenchymal stromal cells as a cellular delivery system for "
    "antitumor drugs and their remote control activation": [
        "Carrier cells", "Cultivation", "Internalization", "Mesenchymal stromal cells",
        "Micro- and nanocapsules", "Migration", "Pharmacokinetics", "Synthesis",
        "Targeted delivery antitumor drugs"],
    "Polymeric micro- and nano-carriers as a universal platform for delivery of biologically "
    "active substances to therapeutically cell populations": [
        "Bioactive substances", "Cells transfection", "Encapsulation",
        "Non-viral delivery systems", "Nucleic acids", "Polymeric capsules"],
    # journals.ioffe.ru/articles/55728, статья на русском, ключевые слова авторские
    "10.21883/pjtf.2023.13.55728.19568": [
        "наноструктуры золото-кремний", "облучение фемтосекундным лазером",
        "широкополосная фотолюминесценция"],
    # journals.ioffe.ru/articles/52740
    "10.21883/pjtf.2022.13.52740.19185n": [
        "наноструктуры", "диоксид титана", "термическое оксидирование", "морфология",
        "дендриты"],
}

# слова, которые без уточнения в скобках ничего не значат: на карточке это шум
DROP = {
    "work", "range", "process", "product", "identification", "realization", "phase", "scale",
    "key", "simple", "feature", "measure", "consistency", "quality", "limit", "zero", "cover",
    "dual", "point", "line", "stack", "control", "tracking", "motion", "block", "spike", "shot",
    "palette", "fundus", "dissection", "risk analysis", "computer graphics", "recursion",
    "constant", "position", "multiplicity", "invariant", "component", "volume", "buffer",
    "separator", "mechanism", "compatibility", "characterization", "yield", "field",
    "distribution", "reduction", "hydrology", "shock", "layer", "core", "stability", "python",
    "cluster", "eclipse", "sting",
}

# названия областей: слишком широкие, чтобы стоять первыми, но выбрасывать их незачем
BROAD = {
    "materials science", "chemistry", "physics", "biology", "computer science", "nanotechnology",
    "optics", "optoelectronics", "engineering", "medicine", "biophysics", "biochemistry",
    "mechanics", "condensed matter physics", "analytical chemistry", "chemical engineering",
    "mathematics", "computational physics", "artificial intelligence", "nanoscience",
    "combinatorial chemistry", "stereochemistry", "medicinal chemistry", "cancer research",
    "materials chemistry", "chemical physics", "molecular physics", "nuclear physics",
    "computational chemistry", "organic chemistry", "inorganic chemistry", "polymer chemistry",
    "biomedical engineering", "nanotechnology and nanoscience",
}

ACRONYM = re.compile(r"^[A-Z0-9][A-Za-z0-9.-]*$")


def lang_of(text):
    """Язык куска текста по письменности: у названия это язык самой статьи."""
    ru = len(re.findall(r"[а-яА-Я]", text or ""))
    en = len(re.findall(r"[a-zA-Z]", text or ""))
    return "ru" if ru > en else "en" if en > ru else ""


def clean_tag(tag):
    """Из концепта OpenAlex делает ключевое слово или пустую строку, если слово пустое."""
    tag = re.sub(r"\s+", " ", tag).strip()
    m = re.fullmatch(r"(.+?)\s*\(([^()]+)\)", tag)
    if m:
        head, note = m.group(1).strip(), m.group(2).strip()
        # в скобках бывает сокращение той же вещи: «... coronavirus 2 (SARS-CoV-2)»
        tag = note if ACRONYM.match(note) and len(note) < len(head) else head
    return "" if tag.lower() in DROP else tag


def clean_tags(tags):
    """Чистит список целиком: без повторов, широкие области в конце."""
    out = []
    for tag in tags:
        tag = clean_tag(tag)
        if tag and tag.lower() not in {t.lower() for t in out}:
            out.append(tag)
    out.sort(key=lambda t: t.lower() in BROAD)
    return out


def from_openalex(doi):
    """Ключевые слова работы. Спрашиваем строго по DOI: поиск по названию находит чужое.
    Тематики (topics) не берем: они про область в целом и к работе часто не относятся."""
    data = openalex(doi, cache="cmt_most_tags", pause=0.2)
    return clean_tags([k["display_name"] for k in data.get("keywords") or []]) if data else []


def load_manual():
    """Теги, вписанные владельцем. Ключ — DOI, а у работ без DOI название целиком."""
    return {k.lower(): v for k, v in load(MANUAL_FILE, {}).items() if v}


def import_md():
    """Забирает ключевые слова, вписанные в content/edit/TAGS_MISSING.md, в content/manual/tags.json."""
    if not MISSING.exists():
        print("нет файла", rel(MISSING))
        return
    manual = load_manual()
    added = 0
    for chunk in MISSING.read_text(encoding="utf-8").split(NL + "## ")[1:]:
        key = re.search(r"<!-- ключ: (.+?) -->", chunk)
        body = re.search(r"### Ключевые слова" + NL + "(.*?)$", chunk, re.S)
        if not key or not body:
            continue
        line = body.group(1).strip()
        line = re.sub(r"^_.*?_$", "", line, flags=re.M).strip()
        tags = [t.strip() for t in re.split(r"[,;" + NL + "]+", line) if t.strip()]
        if tags:
            manual[key.group(1).strip().lower()] = tags
            added += 1
    save(MANUAL_FILE, manual, sort_keys=True)
    print(f"вписано руками: {added}, всего в {MANUAL_FILE.name}: {len(manual)}")


def write_missing(rows):
    """Список работ, у которых с тегами что-то не так, для ручного заполнения."""
    db = load(DB)
    by_doi = {(r.get("doi") or "").lower(): r for r in db["works"] if r.get("doi")}
    out = ["# Работы, которым нужны ключевые слова", "",
           "Здесь работы, у которых тегов нет ни на сайте, ни в OpenAlex, и работы, чьи теги",
           "не на языке статьи. Откройте ссылку, перепишите ключевые слова со страницы статьи",
           "через запятую вместо строки-подсказки. Язык оригинала не меняем, свои слова",
           "не придумываем.", "",
           "Потом: `python tools/publications/tags.py --import-md` перенесет их",
           "в `content/manual/tags.json` и проставит публикациям.", "",
           f"Всего работ: {len(rows)}", ""]
    for doi, title, journal, date, why in rows:
        rec = by_doi.get(doi.lower(), {})
        out += ["## " + (title or "без названия"), "",
                "<!-- ключ: " + (doi or title) + " -->", "",
                "%s, %s. %s" % (journal or "издание не указано", date or "дата не указана",
                                rec.get("authors") or ""), "",
                "Что не так: " + why, "",
                ("https://doi.org/" + doi) if doi else "DOI у работы нет, искать по названию", "",
                "### Ключевые слова", "", "_впишите сюда через запятую_", ""]
    write(MISSING, NL.join(out).rstrip() + NL)
    print(f"список для ручного добора: {rel(MISSING)} ({len(rows)} работ)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="только показать, файл не трогать")
    ap.add_argument("--offline", action="store_true", help="не ходить в OpenAlex, жить на кэше")
    ap.add_argument("--import-md", dest="import_md", action="store_true",
                    help="забрать слова из content/edit/TAGS_MISSING.md и проставить их")
    args = ap.parse_args()

    if args.import_md:
        import_md()

    manual = load_manual()
    pubs = load(PUBLICATIONS)
    cleaned, filled, relang, left = 0, 0, 0, []
    for pub in pubs:
        doi, title = pub.get("doi", "").removeprefix("https://doi.org/"), pub.get("title", "")
        journal, date = pub.get("journal", ""), pub.get("date", "")
        old = pub.get("tags", [])
        own = manual.get(doi.lower()) or manual.get(title.lower()) \
            or MANUAL.get(doi) or MANUAL.get(title)
        new = own or clean_tags(old)
        if not new and not args.offline and doi:
            new = from_openalex(doi)
            if new:
                filled += 1
                print("  добраны теги: " + title[:55] + " -> " + ", ".join(new[:5]))
        # теги на языке статьи: у русской работы русские, у английской английские.
        # Вписанные руками не трогаем, там язык выбрал владелец
        want = lang_of(title)
        if new and not own and want and lang_of(" ".join(new)) not in ("", want):
            other = from_openalex(doi) if want == "en" and doi and not args.offline else []
            if other and lang_of(" ".join(other)) == want:
                print("  теги на язык статьи: " + title[:50] + " -> " + ", ".join(other[:5]))
                new, relang = other, relang + 1
            else:
                left.append((doi, title, journal, date, "теги не на языке статьи, нужны "
                             + ("русские" if want == "ru" else "английские")))
        if not new:
            left.append((doi, title, journal, date, "тегов нет"))
            continue
        if new != old:
            if old:
                cleaned += 1
                gone = [t for t in old if not clean_tag(t)]
                if gone:
                    print("  выброшено: " + ", ".join(gone[:6]))
            pub["tags"] = new
    print("почищено списков: %d, добрано тегов: %d, переведено на язык статьи: %d, "
          "ждут владельца: %d" % (cleaned, filled, relang, len(left)))
    if args.dry:
        return
    save(PUBLICATIONS, pubs)
    print("записано:", rel(PUBLICATIONS))
    write_missing(left)


if __name__ == "__main__":
    main()
