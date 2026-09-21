"""Чистит названия публикаций в data.js от остатков разметки и разорванных формул.

Названия приходят из OpenAlex и Crossref, и в них попадает то, чем издатель размечал
подстрочные индексы и курсив: теги <sub> и <i>, TeX вида CaCO$_3$, странная запись
-=SUB=-2-=/SUB=-. Плюс подстрочный индекс часто отрывается от формулы («CsPbBr 3»),
а иногда наоборот слипаются слова («CO2laser»).

Запуск: python tools/fix_titles.py [--dry]
"""
import argparse
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "js" / "data.js"
NL = chr(10)

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

    text = DATA.read_text(encoding="utf-8")
    start = text.index("window.PUBLICATIONS")
    head, body = text[:start], text[start:]
    changed = 0
    for old in re.findall(r'title: "(.*?)",' + NL, body, re.S):
        new = clean(old)
        if new != old:
            body = body.replace('title: "' + old + '",' + NL, 'title: "' + new + '",' + NL, 1)
            changed += 1
            print("  было:  " + old[:110])
            print("  стало: " + new[:110])
    print("исправлено названий:", changed)
    if changed and not args.dry:
        DATA.write_text(head + body, encoding="utf-8", newline=NL)
        print("записано:", DATA)


main()
