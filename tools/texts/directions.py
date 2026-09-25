"""Выгружает тексты направлений в content/edit/DIRECTIONS_TEXT.md и заливает правки обратно.

Смысл: править длинные тексты удобнее в markdown, а не среди кавычек и запятых в данных.

    python tools/texts/directions.py --export         content/directions.json -> DIRECTIONS_TEXT.md
    python tools/texts/directions.py --import         DIRECTIONS_TEXT.md -> content/directions.json
    python tools/texts/directions.py --import --dry   показать, что изменится

Переносятся название, подзаголовок, абзацы «О направлении», ключевые слова и состав команды.
Заголовок первого экрана (`heroTitle`) в markdown не выносится: там верстка с <em> и <br>,
после смены названия его правим отдельно. Порядок направлений и их адреса (`id`) файл не меняет.
"""
import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib.paths import DIRECTIONS, EDIT
from lib.store import load, rel, save, write

DOC = EDIT / "DIRECTIONS_TEXT.md"
NL = chr(10)
PARA = NL * 2
FIELDS = ("title", "subtitle", "about", "tags", "people")

HEAD = """# Тексты научных направлений

Рабочий файл для правки текстов. Что меняется здесь, переносится в сайт командой
`python tools/texts/directions.py --import`, обратно выгружается `--export`.

Правила те же, что на сайте: без буквы «ё», поменьше тире и двоеточий, ничего не выдумываем
за авторов. Абзац отделяется пустой строкой. Ключевые слова перечисляются через запятую,
люди списком, порядок в команде на сайте все равно задает правило в `main.js`.

Заголовок первого экрана (крупная надпись на фото) здесь не правится, он собирается
из названия отдельно.
"""


def export():
    dirs = load(DIRECTIONS)
    out = [HEAD.strip()]
    for d in dirs:
        part = [f"## {d.get('title', '')}", f"<!-- id: {d['id']} -->",
                f"**Подзаголовок:** {d.get('subtitle', '')}", "### Текст"]
        part += d.get("about", [])
        part += ["### Ключевые слова", ", ".join(d.get("tags", [])), "### Команда",
                 NL.join(f"- {name}" for name in d.get("people", []))]
        out.append(PARA.join(part))
    write(DOC, PARA.join(out).rstrip() + NL)
    print("записано:", rel(DOC), f"({len(dirs)} направлений)")


def parse_doc():
    text = DOC.read_text(encoding="utf-8")
    found = {}
    for chunk in re.split(r"\n## ", text)[1:]:
        chunk = "## " + chunk
        did = re.search(r"<!-- id: ([^\s]+) -->", chunk)
        if not did:
            continue
        title = chunk.splitlines()[0][3:].strip()
        sub = re.search(r"\*\*Подзаголовок:\*\* (.*)", chunk)
        body = re.search(r"### Текст\n(.*?)\n### Ключевые слова\n(.*?)\n### Команда\n(.*?)$", chunk, re.S)
        if not body:
            raise SystemExit(f"в разделе «{title}» не хватает одной из частей: Текст, Ключевые слова, Команда")
        about = [p.strip() for p in body.group(1).strip().split("\n\n") if p.strip()]
        tags = [t.strip() for t in body.group(2).replace("\n", " ").split(",") if t.strip()]
        people = [line[2:].strip() for line in body.group(3).splitlines() if line.startswith("- ")]
        found[did.group(1)] = {"title": title, "subtitle": sub.group(1).strip() if sub else "",
                               "about": about, "tags": tags, "people": people}
    return found


def import_(dry):
    edits = parse_doc()
    dirs = load(DIRECTIONS)
    changed = []
    for d in dirs:
        new = edits.get(d["id"])
        if not new:
            continue
        what = []
        for name in FIELDS:
            empty = [] if name in ("about", "tags", "people") else ""
            if new[name] != d.get(name, empty):
                d[name] = new[name]
                what.append(name)
        # размер команды не хранится отдельно, он всегда равен списку людей
        if new["people"] and d.get("team") != len(new["people"]):
            d["team"] = len(new["people"])
            what.append("team")
        if what:
            changed.append(d["id"] + ": " + ", ".join(what))
    print("изменилось:", "; ".join(changed) if changed else "ничего")
    if changed and not dry:
        save(DIRECTIONS, dirs)
        print("записано:", rel(DIRECTIONS))
        print("дальше: python tools/smoke.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", action="store_true")
    ap.add_argument("--import", dest="imp", action="store_true")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    if args.export:
        export()
    elif args.imp:
        import_(args.dry)
    else:
        ap.error("нужен --export или --import")


if __name__ == "__main__":
    main()
