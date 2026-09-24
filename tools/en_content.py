"""Переводы данных для английской версии: направления, люди и новости.

Тексты ведутся в markdown, как русские в docs/DIRECTIONS_TEXT.md:
    docs/EN_DIRECTIONS.md   направления: название, заголовок первого экрана, подзаголовок, текст, ключевые слова
    docs/EN_PEOPLE.md       люди: имя латиницей, степень и должность по-английски
    docs/EN_NEWS.md         новости: заголовок, анонс, вступление, цитата, заключение

    python tools/en_content.py --people   # дописать в EN_PEOPLE.md новых людей из data.js
    python tools/en_content.py --news     # дописать в EN_NEWS.md заготовки новых новостей из анкеты
    python tools/en_content.py --import   # собрать assets/js/en-content.js из всех трех файлов

--people ничего не затирает: у тех, кто уже есть в таблице, строка остается как была
(владелец мог ее поправить). Новым людям степень и должность переводятся по словарю ниже,
имя транслитерируется и помечается «проверить»: как человек пишет имя в статьях, знает он сам.
После --import нужно пересобрать страницы (build_en.py) и метки версий (bump_assets.py).
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIRS_MD = ROOT / "docs" / "EN_DIRECTIONS.md"
PEOPLE_MD = ROOT / "docs" / "EN_PEOPLE.md"
NEWS_MD = ROOT / "docs" / "EN_NEWS.md"
OUT = ROOT / "assets" / "js" / "en-content.js"
NL = "\n"

# английские названия степеней, ступеней и должностей, как на английском сайте ИТМО
DEGREES = [
    (r"^доктор физико-математических наук$", "Doctor of Sciences in Physics and Mathematics"),
    (r"^кандидат физико-математических наук$", "PhD in Physics and Mathematics"),
    (r"^кандидат технических наук$", "PhD in Engineering"),
    (r"^кандидат химических наук$", "PhD in Chemistry"),
    (r"^кандидат биологических наук$", "PhD in Biology"),
    (r"^аспирант (\d)-го года$", lambda m: f"{ordinal(m[1])}-year PhD student"),
    (r"^магистр (\d)-го года$", lambda m: f"{ordinal(m[1])}-year master’s student"),
    (r"^бакалавр (\d)-го года$", lambda m: f"{ordinal(m[1])}-year bachelor’s student"),
    (r"^аспирант$", "PhD student"),
    (r"^магистр$", "master’s student"),
    (r"^бакалавр$", "bachelor’s student"),
    (r"^студент$", "student"),
]
POSTS = {
    "главный научный сотрудник": "chief researcher",
    "ведущий научный сотрудник": "leading researcher",
    "старший научный сотрудник": "senior researcher",
    "научный сотрудник": "researcher",
    "младший научный сотрудник": "junior researcher",
    "инженер": "engineer",
    "лаборант": "laboratory assistant",
}
TRANSLIT = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
                    ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s",
                     "t", "u", "f", "kh", "ts", "ch", "sh", "shch", "", "y", "", "e", "yu", "ya"]))


def ordinal(n):
    return {"1": "1st", "2": "2nd", "3": "3rd"}.get(n, f"{n}th")


def translit(name):
    out = "".join(TRANSLIT.get(c.lower(), c) if c.lower() in TRANSLIT else c for c in name)
    return " ".join(w[:1].upper() + w[1:] for w in out.split(" "))


def en_degree(ru):
    for pat, rep in DEGREES:
        m = re.match(pat, ru or "")
        if m:
            return rep(m) if callable(rep) else rep
    return ""


def load_data():
    """PEOPLE и id направлений из data.js через node: в файле JS, а не JSON"""
    js = ("global.window = {}; eval(require('fs').readFileSync(process.argv[1], 'utf8'));"
          "console.log(JSON.stringify({ people: window.PEOPLE, dirs: window.DIRECTIONS.map((d) => d.id),"
          " news: window.NEWS.map((n) => ({ id: n.id, title: n.title, date: n.date })) }))")
    res = subprocess.run(["node", "-e", js, str(ROOT / "assets" / "js" / "data.js")],
                         capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(res.stdout)


# ---------- люди ----------

ROW = re.compile(r"^\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$")


def read_people():
    rows = {}
    if not PEOPLE_MD.exists():
        return rows
    for line in PEOPLE_MD.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if m and not m[1].startswith(("Имя", "---", ":--")):
            rows[m[1]] = {"name": m[2], "degree": m[3], "post": m[4], "note": m[5]}
    return rows


def write_people(people):
    rows = read_people()
    added = 0
    for ru, p in people.items():
        if ru in rows:
            continue
        rows[ru] = {"name": translit(ru), "degree": en_degree(p.get("degree")),
                    "post": POSTS.get(p.get("post", ""), ""), "note": "проверить имя"}
        added += 1
    head = ("# People in English\n\n"
            "Имя латиницей, степень и должность по-английски для карточек команды на английских страницах.\n"
            "Имена взяты так, как люди подписываются в своих статьях (по авторам публикаций на сайте).\n"
            "Пометка «проверить имя» значит, что статей с этим человеком на сайте нет и имя транслитерировано:\n"
            "его стоит сверить с самим человеком, после этого пометку можно стереть.\n\n"
            "Новых людей из книги сотрудников дописывает `python tools/en_content.py --people`, строки\n"
            "уже вписанных людей он не трогает. На сайт таблица попадает через `--import`.\n\n"
            "| Имя | Name | Degree | Post | Заметка |\n|---|---|---|---|---|\n")
    body = "".join(f"| {ru} | {r['name']} | {r['degree']} | {r['post']} | {r['note']} |\n" for ru, r in rows.items())
    PEOPLE_MD.write_text(head + body, encoding="utf-8", newline="\n")
    print(f"{PEOPLE_MD.relative_to(ROOT)}: людей {len(rows)}, новых {added}")


# ---------- направления ----------

def read_directions():
    text = DIRS_MD.read_text(encoding="utf-8")
    out = {}
    for part in re.split(r"(?m)^## ", text)[1:]:
        title, _, rest = part.partition(NL)
        m = re.search(r"<!-- id: ([\w-]+) -->", rest)
        if not m:
            continue
        field = lambda name: (re.search(rf"\*\*{name}:\*\*\s*(.+)", rest) or [None, ""])[1].strip()
        body = re.search(r"### Text\s*\n(.*?)(?=\n### |\Z)", rest, re.S)
        kw = re.search(r"### Keywords\s*\n(.*?)(?=\n### |\n## |\Z)", rest, re.S)
        entry = {"title": title.strip()}
        if field("Hero title"):
            entry["heroTitle"] = field("Hero title")
        if field("Subtitle"):
            entry["subtitle"] = field("Subtitle")
        if body:
            entry["about"] = [p.strip().replace(NL, " ") for p in re.split(r"\n\s*\n", body[1].strip()) if p.strip()]
        if kw:
            entry["tags"] = [t.strip() for t in kw[1].replace(NL, " ").split(",") if t.strip()]
        out[m[1]] = entry
    return out


# ---------- новости ----------

SECTIONS = {"Lead": "lead", "Quote": "quote", "Note": "note"}


def paras(text):
    return [p.strip().replace(NL, " ") for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def read_news():
    """Новость без текста (заготовка) пропускается: на сайте она останется русской"""
    out = {}
    if not NEWS_MD.exists():
        return out
    for part in re.split(r"(?m)^## ", NEWS_MD.read_text(encoding="utf-8"))[1:]:
        title, _, rest = part.partition(NL)
        m = re.search(r"<!-- id: ([\w-]+) -->", rest)
        card = re.search(r"\*\*Card:\*\*\s*(.+)", rest)
        if not m or not title.strip() or title.strip().startswith("TODO") or not card:
            continue
        body = {}
        for head, key in SECTIONS.items():
            sec = re.search(rf"### {head}\s*\n(.*?)(?=\n### |\Z)", rest, re.S)
            if sec and paras(sec[1]):
                body[key] = paras(sec[1])
        out[m[1]] = {"title": title.strip(), "text": card[1].strip(), "body": body}
    return out


def write_news_stubs(news):
    text = NEWS_MD.read_text(encoding="utf-8")
    have = set(re.findall(r"<!-- id: ([\w-]+) -->", text))
    new = [n for n in news if n["id"] not in have]
    for n in new:
        text = text.rstrip() + (f"\n\n## TODO {n['date']}: {re.sub('<br>', '', n['title'])}\n\n<!-- id: {n['id']} -->\n\n"
                                "**Card:** \n\n### Lead\n\n### Note\n")
    NEWS_MD.write_text(text + "\n", encoding="utf-8", newline="\n")
    print(f"{NEWS_MD.relative_to(ROOT)}: новых заготовок {len(new)}" + (" (" + ", ".join(n["id"] for n in new) + ")" if new else ""))


def do_import(data):
    dirs = read_directions()
    people = {ru: {k: v for k, v in (("name", r["name"]), ("degree", r["degree"]), ("post", r["post"])) if v}
              for ru, r in read_people().items()}
    news = read_news()
    missing_dirs = [d for d in data["dirs"] if d not in dirs]
    missing_news = [n["id"] for n in data["news"] if n["id"] not in news]
    missing_people = [p for p in data["people"] if p not in people]
    cyr = [f"{k}: {v[:60]}" for k, e in {**dirs, **news}.items()
           for v in [json.dumps(e, ensure_ascii=False)] if re.search(r"[А-Яа-яЁё]", v)]
    js = ("/* Собрано tools/en_content.py из docs/EN_DIRECTIONS.md и docs/EN_PEOPLE.md, руками не править.\n"
          "   Переводы направлений, людей и новостей для английской версии, их подставляет tr() из layout.js. */\n"
          f"Object.assign(window.EN.directions, {json.dumps(dirs, ensure_ascii=False, indent=2)});\n"
          f"Object.assign(window.EN.people, {json.dumps(people, ensure_ascii=False, indent=2)});\n"
          f"Object.assign(window.EN.news, {json.dumps(news, ensure_ascii=False, indent=2)});\n")
    OUT.write_text(js, encoding="utf-8", newline="\n")
    print(f"{OUT.relative_to(ROOT)}: направлений {len(dirs)}, людей {len(people)}, новостей {len(news)}")
    if missing_news:
        print("  ~ нет английского текста у новостей (запустите --news и переведите):", ", ".join(missing_news))
    if missing_dirs:
        print("  ~ нет английского текста у направлений:", ", ".join(missing_dirs))
    if missing_people:
        print("  ~ нет в EN_PEOPLE.md (запустите --people):", ", ".join(missing_people))
    if cyr:
        print("  ! в английских текстах осталась кириллица:", *cyr, sep="\n    ")
        return 1
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--people", action="store_true")
    ap.add_argument("--news", action="store_true")
    ap.add_argument("--import", dest="imp", action="store_true")
    args = ap.parse_args()
    data = load_data()
    code = 0
    if args.people:
        write_people(data["people"])
    if args.news:
        write_news_stubs(data["news"])
    if args.imp:
        code = do_import(data)
    if not (args.people or args.news or args.imp):
        ap.print_help()
    sys.exit(code)
