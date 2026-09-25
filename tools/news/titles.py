"""Заголовки новостей: выгрузка на вычитку и загрузка обратно в данные.

Заголовок из анкеты и заголовок на сайте живут отдельно: правки владельца лежат
в content/manual/news_titles.json и при переносе анкеты побеждают, а заголовок из анкеты
остается в content/news.json в поле formTitle.

Правка идет через content/edit/NEWS_TITLES_LINES.md:

    python tools/news/titles.py --export    выгрузить заголовки построчно
    python tools/news/titles.py --import    залить правки обратно (--dry покажет разницу)

В файле правится не строка заголовка, а его разбивка по строкам: под каждой новостью блок
«в карточке» с пронумерованными строками. Разбивка меряется в браузере на настоящей странице,
потому что перенос зависит от шрифта и от неразрывных пробелов, которые расставляет layout.js.
Считать знаки для этого мало. Ключ --no-lines пропускает замер, если браузера под рукой нет.
"""
import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import build
from lib.browser import launch
from lib.paths import EDIT, MANUAL_NEWS_TITLES as TITLES, NEWS as STORE
from lib.server import serve
from lib.store import load, rel, save, write
from news.form import write_store

DOC = EDIT / "NEWS_TITLES_LINES.md"   # правится построчно, см. export()
NL = chr(10)
LINES = 3      # столько строк отведено заголовку в карточке и в новости месяца

SPLIT_JS = """(titles) => {
  const lines = (el, text) => {
    const clamp = el.style.webkitLineClamp;
    el.style.webkitLineClamp = 'unset';
    el.textContent = text;
    const node = el.firstChild;
    const out = [];
    let top = null, cur = [];
    let from = 0;
    for (const w of text.split(' ').filter(Boolean)) {
      const at = text.indexOf(w, from);
      from = at + w.length;
      const r = document.createRange();
      r.setStart(node, at);
      r.setEnd(node, at + w.length);
      const y = Math.round(r.getBoundingClientRect().top);
      if (top === null || Math.abs(y - top) < 3) { cur.push(w); top = y; }
      else { out.push(cur.join(' ')); cur = [w]; top = y; }
    }
    if (cur.length) out.push(cur.join(' '));
    el.style.webkitLineClamp = clamp;
    return out;
  };
  // <br> в заголовке ломает строку жестко, поэтому части меряем отдельно
  const split = (el, text) => text.split(/<\\/?br\\s*\\/?>/i)
    .map((part) => part.trim()).filter(Boolean)
    .flatMap((part) => lines(el, part));
  const card = document.querySelector('.news-all .news-card__title');
  const big = document.querySelector('.featured__title');
  const res = {};
  for (const t of titles) res[t.id] = {card: split(card, t.title), top: split(big, t.title)};
  return res;
}"""


def measure(items):
    """Как каждый заголовок ляжет по строкам: меряем в браузере на ширине 1920."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("нет playwright, разбивка по строкам пропущена")
        return {}

    # меряем на собранном сайте: без сборки нет файла данных, и страница новостей пустая
    if not build.build(quiet=True):
        print("сайт не собрался, разбивка по строкам пропущена")
        return {}
    with serve() as base, sync_playwright() as pw:
        browser = launch(pw)
        page = browser.new_context(viewport={"width": 1920, "height": 1080},
                                   reduced_motion="reduce").new_page()
        page.goto(base + "news.html", wait_until="load")
        page.wait_for_timeout(500)
        rows = page.evaluate(SPLIT_JS, [{"id": n["id"], "title": n["title"]} for n in items])
        browser.close()
    return rows


def show(lines):
    """Строки заголовка так, как они встанут на сайте. Лишние помечаем.

    Неразрывные пробелы после предлогов ставит сайт, в файле они только мешают.
    """
    return [f"    {i}  {line.replace(chr(160), ' ')}"
            + ("" if i <= LINES else "   <-- не поместится, обрежется")
            for i, line in enumerate(lines, 1)]


def export(items, with_lines=True):
    own = load(TITLES, {})
    rows = measure(items) if with_lines else {}
    out = ["# Заголовки новостей", "",
           "Правится блок «в карточке»: слова, их порядок и то, по каким строкам они лягут.",
           f"Строк должно быть не больше {LINES}, лишние на сайте обрежутся многоточием.",
           "Номера в начале строк можно не трогать, при чтении они пересчитываются.", "",
           "Блок «в новости месяца» показан для той новости, что стоит крупно наверху страницы.",
           "Он не правится, а пересчитывается: колонка там уже, и строки ложатся иначе.", "",
           "Разбивка снята в браузере на ширине 1920. Если ваше деление на строки совпадает",
           "с тем, как текст ложится сам, заголовок сохраняется обычной строкой. Если нет,",
           "в нужных местах ставится жесткий перенос, он работает на широком экране,",
           "а в окне новости и на телефоне скрывается и текст переносится сам.", "",
           "Потом: `python tools/news/titles.py --import`, дальше `--export` пересчитает строки.", ""]
    for n in items:
        head = f"## {n['id']} · {n['date']} · {n['tag']}"
        if n.get("featured"):
            head += " · новость месяца"
        out += [head, ""]
        if n.get("formTitle") and n["formTitle"] != n["title"]:
            out.append(f"<!-- в анкете: {n['formTitle']} -->")
        row = rows.get(n["id"])
        if not row:
            out += [f"сейчас: {n['title']}", ""]
            continue
        out += ["в карточке:"] + show(row["card"])
        if n.get("featured"):
            out += ["", "в новости месяца:"] + show(row["top"])
        out.append("")
    write(DOC, NL.join(out).rstrip() + NL)
    print(f"выгружено заголовков: {len(items)} в {rel(DOC)}")
    print(f"своих заголовков сейчас: {len(own)}")
    long = [n["id"] for n in items if len(rows.get(n["id"], {}).get("card", [])) > LINES]
    if long:
        print(f"не встают в {LINES} строки ({len(long)}): " + ", ".join(long))


def read_doc():
    """Что написано в блоках «в карточке»: {ид новости: [строки заголовка]}."""
    blocks = {}
    for chunk in DOC.read_text(encoding="utf-8").split(NL + "## ")[1:]:
        key = chunk.split(NL, 1)[0].split(" · ")[0].strip()
        part = chunk.split(NL + "в карточке:" + NL, 1)
        if len(part) < 2:
            plain = re.search(r"^сейчас: (.+)$", chunk, re.M)
            if plain:
                blocks[key] = [clean(plain.group(1))]
            continue
        lines = []
        for line in part[1].splitlines():
            if not line.strip():
                break
            got = re.match(r"^\s*\d*\s*(.+?)(?:\s{2,}<--.*)?$", line)
            if got:
                lines.append(clean(got.group(1)))
        if lines:
            blocks[key] = lines
    return blocks


def clean(text):
    """Неразрывные пробелы ставит сайт, «ё» на сайте не пишем."""
    return re.sub(r"\s+", " ", text.replace(" ", " ")).strip() \
        .replace("ё", "е").replace("Ё", "Е")


def import_md(items, dry):
    own = load(TITLES, {})
    by_id = {n["id"]: n for n in items}
    blocks = {k: v for k, v in read_doc().items() if k in by_id}
    # как текст лег бы сам, без жестких переносов: где деление владельца совпало с этим,
    # заголовок остается обычной строкой, иначе проставляем перенос
    plain = {k: " ".join(v) for k, v in blocks.items()}
    natural = measure([{"id": k, "title": v} for k, v in plain.items()])

    changed, long = [], []
    for key, lines in blocks.items():
        own_lines = [clean(x) for x in natural.get(key, {}).get("card", [])]
        title = plain[key] if own_lines == lines else " <br> ".join(lines)
        if len(lines) > LINES:
            long.append(key)
        if title and title != by_id[key]["title"]:
            changed.append((key, by_id[key]["title"], title))
            own[key] = title
            by_id[key]["title"] = title
    for key, was, now in changed:
        print(f"  {key}:")
        print(f"      было: {was}")
        print(f"      стало: {now}")
    print(f"переписано заголовков: {len(changed)}")
    if long:
        print(f"строк больше {LINES}, на сайте обрежется ({len(long)}): " + ", ".join(long))
    if dry:
        print("сухой прогон, файлы не тронуты")
        return
    save(TITLES, own, sort_keys=True)
    write_store(items)
    print("записано:", rel(TITLES), "и", rel(STORE))
    print("дальше: python tools/news/titles.py --export (пересчитать строки) и python tools/smoke.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", action="store_true")
    ap.add_argument("--import", dest="load_md", action="store_true")
    ap.add_argument("--no-lines", action="store_true", help="не мерить разбивку по строкам")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    items = load(STORE)
    if args.load_md:
        import_md(items, args.dry)
    else:
        export(items, not args.no_lines)


if __name__ == "__main__":
    main()
