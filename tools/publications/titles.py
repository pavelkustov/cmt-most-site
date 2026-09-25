"""Чистит названия публикаций сайта от остатков разметки и разорванных формул.

Названия приходят из OpenAlex и Crossref, и в них попадает то, чем издатель размечал
подстрочные индексы и курсив: теги <sub> и <i>, TeX вида CaCO$_3$, странная запись
-=SUB=-2-=/SUB=-. Плюс подстрочный индекс часто отрывается от формулы («CsPbBr 3»),
а иногда наоборот слипаются слова («CO2laser»).

Запуск: python tools/publications/titles.py [--dry]
"""
import argparse
import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib.paths import PUBLICATIONS
from lib.store import load, rel, save

# то, что правилами не берется: разбираем поштучно
# цепочка символов химических элементов: Cs, Pb, Br, Ti, O и так далее
FORMULA_GAP = re.compile(r"\b((?:[A-Z][a-z]?){1,6})\s+([0-9]+(?:\.[0-9]+)?[+-]?)(?=\W|$)")

MANUAL = {
    "Luminescent rare earth vanadate nanoparticles doped with Eu3+and Bi3for sensing and imaging applications":
        "Luminescent rare earth vanadate nanoparticles doped with Eu3+ and Bi3+ for sensing and imaging applications",
    "3D express crystallization of Foturan glass at CO2laser annealing on defects produced by picosecond laser":
        "3D express crystallization of Foturan glass at CO2 laser annealing on defects produced by picosecond laser",
    # в записи слиплись английский и русский варианты названия, оставляем английский
    "Crystallization of robotic swarms in a parabolic potential,Исследование кристаллизации "
    "скопления роботов в параболическом потенциале":
        "Crystallization of robotic swarms in a parabolic potential",
    # на странице издателя название с пробелом: «micro- and nano-carriers»
    "Polymeric micro-and nano-carriers as a universal platform for delivery of biologically "
    "active substances to therapeutically cell populations":
        "Polymeric micro- and nano-carriers as a universal platform for delivery of biologically "
        "active substances to therapeutically cell populations",
}


def clean(title):
    text = title
    for old, new in MANUAL.items():
        if text == old:
            return new
    # запись подстрочного индекса, которую переводные журналы отдают как -=SUB=-2-=/SUB=-
    text = re.sub(r"-=SUB=-([^=]*)-=/SUB=-", r"\1", text)
    text = re.sub(r"-=SUP=-([^=]*)-=/SUP=-", r"^\1", text)
    text = re.sub(r"<[^>]+>", "", text)          # <sub>, <i> и прочая разметка издателя
    text = html.unescape(text)
    text = re.sub(r"[$]_?[{]?([0-9]+)[}]?[$]", r"\1", text)   # CaCO$_3$
    text = text.replace("$", "")
    # подстрочный индекс, оторванный от формулы: «CsPbBr 3», «Mg 2+», «Eu 3+».
    # приклеиваем только к химической формуле, то есть цепочке символов элементов,
    # иначе пострадают «DNAzyme 10-23» и «Pumped 946/1030 nm»
    text = FORMULA_GAP.sub(lambda m: m.group(1) + m.group(2), text)
    text = re.sub(r"([0-9][+-]?)\s+([/-])(?=[A-Za-z0-9])", r"\1\2", text)   # «AgInS2 /ZnS», «Mg2+ -Release»
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    pubs = load(PUBLICATIONS)
    changed = 0
    for pub in pubs:
        new = clean(pub["title"])
        if new != pub["title"]:
            print("  было:  " + pub["title"][:110])
            print("  стало: " + new[:110])
            pub["title"] = new
            changed += 1
    print("исправлено названий:", changed)
    if changed and not args.dry:
        save(PUBLICATIONS, pubs)
        print("записано:", rel(PUBLICATIONS))


if __name__ == "__main__":
    main()
