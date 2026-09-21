"""Дописывает авторов публикациям, у которых их нет, по Crossref и OpenAlex.

Часть работ пришла на сайт без списка авторов: у переводных и конференционных записей
источник иногда отдает только название. Сначала спрашиваем Crossref, потом OpenAlex.
Что не нашлось нигде, лежит в словаре MANUAL: это списки, переписанные со страницы
издателя руками, с указанием источника.

Заодно чинится порядок слов: arXiv и Figshare отдают авторов как «Фамилия, Имя»,
и на сайте список читается как вдвое большее число людей.

Запуск: python tools/fill_authors.py [--dry]
"""
import argparse
import json
import pathlib
import re
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "js" / "data.js"
UA = {"User-Agent": "cmt-most-site/1.0 (mailto:bridge@metalab.ifmo.ru)"}
NL = chr(10)

# авторов этих работ нет ни в Crossref, ни в OpenAlex: списки взяты со страницы издателя
# (21.09.2026). Ключ — DOI, а у работ без DOI название целиком.
MANUAL = {
    # opticjourn.ru/ru/abstract/2026-93-3-33-39
    "10.17586/1023-5086-2026-93-03-33-39": "А.О. Ларин, А.А. Ермина, Ю.А. Жарова, Д.А. Зуев",
    # cttjournal.com/en/article/study-of-multipotent-mesenchymal-stromal-cells-as-a-cellular-delivery-system-for-antitumor-drugs-and
    "Study of multipotent mesenchymal stromal cells as a cellular delivery system for "
    "antitumor drugs and their remote control activation":
        "Oleksii O. Peltek, Timofey E. Karpov, Yana V. Tarakanchikova, Mikhail V. Zyuzin, "
        "Albert R. Muslimov",
    # cttjournal.com/en/article/polymeric-micro-and-nano-carriers-as-a-universal-platform-for-delivery-of-biologically-active
    "Polymeric micro- and nano-carriers as a universal platform for delivery of biologically "
    "active substances to therapeutically cell populations":
        "Albert R. Muslimov, Tatyana V. Mashel, Oleksii O. Peltek, Mikhail A. Trofimov, "
        "Igor S. Sergeev, Yana V. Tarakanchikova, Alexander A. Goncharenko, Kirill V. Lepik, "
        "Mikhail V. Zyuzin, Alexander S. Timin",
    # joam.inoe.ro/articles/laser-induced-phase-structure-changes-psc-in-glass-like-materials/
    "Laser-induced phase-structure changes (PSC) in glass-like materials":
        "V. Veiko, E. Ageev, A.V. Kolobov, J. Tominaga",
}

INITIAL = re.compile(r"[^\W\d_][a-zа-яё]{0,2}\.")


def family_like(token):
    """Фамилия это одно слово с большой буквы и без точек: «Buzakov», «Cuscunà», «Möhwald»."""
    return bool(token) and token[0].isupper() and all(c.isalpha() or c in "'’-" for c in token)


def given_like(token):
    """Имя это такое же слово, за которым может стоять инициал отчества: «Alexander A.»"""
    parts = token.split()
    if not parts or not family_like(parts[0]):
        return False
    return len(parts) == 1 or (len(parts) == 2 and bool(INITIAL.fullmatch(parts[1])))


def unswap(line):
    """«Фамилия, Имя, Фамилия, Имя» превращает в «Имя Фамилия, Имя Фамилия».
    Трогает только строки, которые честно делятся на такие пары: список вида
    «А.В. Любимова, Н.А. Жесткий» или «Poroykov, A., Untila, G.» остается как есть."""
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 4 or len(parts) % 2 or not all(parts):
        return line
    pairs = list(zip(parts[::2], parts[1::2]))
    if not all(family_like(family) and given_like(given) for family, given in pairs):
        return line
    return ", ".join(given + " " + family for family, given in pairs)


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as f:
            return json.load(f)
    except Exception:
        return {}


def from_crossref(doi):
    rows = (get("https://api.crossref.org/works/" + doi).get("message") or {}).get("author") or []
    names = [" ".join(x for x in (a.get("given"), a.get("family")) if x).strip() for a in rows]
    return [n for n in names if n]


def from_openalex(doi):
    rows = get("https://api.openalex.org/works/doi:" + doi).get("authorships") or []
    return [a["author"]["display_name"] for a in rows if (a.get("author") or {}).get("display_name")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    text = DATA.read_text(encoding="utf-8")
    start = text.index("window.PUBLICATIONS")
    body = text[start:text.index(NL + "];", start)]   # только публикации, новости не трогаем
    filled, fixed, left = 0, 0, []
    for block in re.findall(NL + "  [{].*?" + NL + "  [}],", body, re.S):
        got = re.search(r'authors: "([^"]*)"', block)
        title = (re.search(r'title: "(.*?)",' + NL, block, re.S) or [None, ""])[1]
        doi = (re.search(r'doi: "https://doi\.org/([^"]+)"', block) or [None, ""])[1]
        if got and got.group(1).strip():
            line = unswap(got.group(1))
            if line != got.group(1):
                text = text.replace(block, block.replace(
                    got.group(0), "authors: " + json.dumps(line, ensure_ascii=False), 1), 1)
                fixed += 1
                print("  порядок слов было:  " + got.group(1)[:90])
                print("               стало: " + line[:90])
            continue
        manual = MANUAL.get(doi) or MANUAL.get(title)
        names = [manual] if manual else []
        if not names:
            names = (from_crossref(doi) or from_openalex(doi)) if doi else []
            time.sleep(0.2)
        if not names:
            left.append((doi, title))
            continue
        line = ", ".join(names)
        if got:
            new = block.replace(got.group(0), 'authors: ' + json.dumps(line, ensure_ascii=False), 1)
        else:
            new = block.replace(NL + "    tags:", NL + "    authors: "
                                + json.dumps(line, ensure_ascii=False) + "," + NL + "    tags:", 1)
        text = text.replace(block, new, 1)
        filled += 1
        print("  " + title[:60] + " -> " + line[:70])

    print("дописано авторов: %d, поправлен порядок слов: %d, осталось без авторов: %d"
          % (filled, fixed, len(left)))
    for doi, title in left:
        print("   %-38s %s" % (doi or "без DOI", title[:70]))
    if (filled or fixed) and not args.dry:
        DATA.write_text(text, encoding="utf-8", newline=NL)
        print("записано:", DATA)


main()
