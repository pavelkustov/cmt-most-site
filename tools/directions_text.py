"""Выгружает тексты направлений в docs/DIRECTIONS_TEXT.md и заливает правки обратно в data.js.

Смысл: править длинные тексты удобнее в markdown, а не среди кавычек и запятых в данных.

    python tools/directions_text.py --export   # data.js -> docs/DIRECTIONS_TEXT.md
    python tools/directions_text.py --import   # docs/DIRECTIONS_TEXT.md -> data.js
    python tools/directions_text.py --import --dry   # показать, что изменится

Переносятся название, подзаголовок, абзацы «О направлении», ключевые слова и состав команды.
Заголовок первого экрана (`heroTitle`) в markdown не выносится: там верстка с <em> и <br>,
после смены названия его правим отдельно. Порядок направлений и их адреса (`id`) файл не меняет.
"""
import argparse
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "js" / "data.js"
DOC = ROOT / "docs" / "DIRECTIONS_TEXT.md"
NL = chr(10)
PARA = NL * 2

HEAD = """# Тексты научных направлений

Рабочий файл для правки текстов. Что меняется здесь, переносится в сайт командой
`python tools/directions_text.py --import`, обратно выгружается `--export`.

Правила те же, что на сайте: без буквы «ё», поменьше тире и двоеточий, ничего не выдумываем
за авторов. Абзац отделяется пустой строкой. Ключевые слова перечисляются через запятую,
люди списком, порядок в команде на сайте все равно задает правило в `main.js`.

Заголовок первого экрана (крупная надпись на фото) здесь не правится, он собирается
из названия отдельно.

"""


def blocks(text):
    start = text.index("window.DIRECTIONS = [") + len("window.DIRECTIONS = [")
    end = text.index("\n];", start)
    return text[:start], re.findall(r"\n  \{.*?\n  \},", text[start:end], re.S), text[end:]


def field(block, name):
    m = re.search(name + r": (\[.*?\n    \]|\[[^\]]*\]|\".*?\"),\n", block, re.S)
    return m.group(1) if m else ""


def paras(block):
    m = re.search(r"about: \[(.*?)\n    \],", block, re.S)
    return [json.loads(x) for x in re.findall(r'\n      ("[^"]*"),', (m.group(1) + ",") if m else "")]


def value(block, name):
    """Значение поля; у направления без ключевых слов или команды поля может не быть вовсе."""
    raw = field(block, name)
    if raw:
        return json.loads(raw)
    return [] if name in ("tags", "people", "about") else ""


def export():
    _, dirs, _ = blocks(DATA.read_text(encoding="utf-8"))
    out = [HEAD.strip()]
    for b in dirs:
        did = re.search(r'id: "([^"]+)"', b).group(1)
        part = [f"## {value(b, 'title')}", f"<!-- id: {did} -->",
                f"**Подзаголовок:** {value(b, 'subtitle')}", "### Текст"]
        part += paras(b)
        part += ["### Ключевые слова", ", ".join(value(b, "tags")), "### Команда",
                 NL.join(f"- {name}" for name in value(b, "people"))]
        out.append(PARA.join(part))
    DOC.write_text(PARA.join(out).rstrip() + NL, encoding="utf-8", newline=NL)
    print("записано:", DOC, f"({len(dirs)} направлений)")


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


def put(block, name, value_):
    dumped = json.dumps(value_, ensure_ascii=False)
    if name == "about":
        body = "".join(f"      {json.dumps(p, ensure_ascii=False)}," + NL for p in value_)
        return re.sub(r"about: \[.*?\n    \],", "about: [" + NL + body + "    ],", block, flags=re.S, count=1)
    if name in ("tags", "people"):
        if re.search(name + r": \[", block):
            return re.sub(name + r": \[[^\]]*\]", f"{name}: {dumped}", block, count=1)
        # поля не было: у направления, где ключевые слова или команду еще не заполнили
        return block.replace(NL + "  },", NL + f"    {name}: {dumped}," + NL + "  },")
    return re.sub(name + r": .*?," + NL, f"{name}: {dumped}," + NL, block, count=1)


def import_():
    edits = parse_doc()
    text = DATA.read_text(encoding="utf-8")
    head, dirs, tail = blocks(text)
    result, changed = [], []
    for b in dirs:
        did = re.search(r'id: "([^"]+)"', b).group(1)
        new = edits.get(did)
        if not new:
            result.append(b)
            continue
        out, what = b, []
        for name in ("title", "subtitle", "about", "tags", "people"):
            before = paras(out) if name == "about" else value(out, name)
            if new[name] != before:
                out = put(out, name, new[name])
                what.append(name)
        # размер команды не хранится отдельно, он всегда равен списку людей
        if new["people"]:
            size = "team: %d" % len(new["people"])
            if re.search(r"team: \d+", out):
                out = re.sub(r"team: \d+", size, out, count=1)
            else:  # у направления, которое заполнили впервые, поля team еще нет
                out = out.replace(NL + "  },", NL + "    " + size + "," + NL + "  },")
                what.append("team")
        if what:
            changed.append(did + ": " + ", ".join(what))
        result.append(out)
    print("изменилось:", "; ".join(changed) if changed else "ничего")
    return head, result, tail, changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", action="store_true")
    ap.add_argument("--import", dest="imp", action="store_true")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    if args.export:
        export()
    elif args.imp:
        head, dirs, tail, changed = import_()
        if changed and not args.dry:
            DATA.write_text(head + "".join(dirs) + tail, encoding="utf-8", newline="\n")
            print("записано:", DATA)
            print("дальше: python tools/bump_assets.py и python tools/smoke.py")
    else:
        ap.error("нужен --export или --import")


main()
