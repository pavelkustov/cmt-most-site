"""Собирает сайт в папку dist: ее и выкладываем на хостинг, целиком и только ее.

    python tools/build.py                              адрес сайта из content/site.json
    python tools/build.py --url https://bridge.itmo.ru/   собрать под другой адрес (переезд)

Что делает по порядку:
1. копирует site/ в dist/;
2. пишет данные из content/*.json в assets/js: data.js, abstracts.js, citations.js, en-content.js;
3. подставляет адрес сайта: {{SITE_URL}} в ссылках для поисковиков и соцсетей,
   {{SITE_PATH}} в теге base страницы «не найдено»;
4. собирает английские страницы en/ из русских (tools/lib/english_pages.py);
5. пишет sitemap.xml: главные страницы и направления, у которых есть описание;
6. ставит у CSS и JS метку версии ?v=хэш, иначе браузеры до 10 минут держат старый кэш.

Нужен только Python, без сторонних пакетов: сборка идет и на машине владельца, и в GitHub Actions.
"""
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import english_pages
from lib.paths import (ABSTRACTS, CITATIONS, DIRECTIONS, DIST, ENGLISH, NEWS, PEOPLE, PUBLICATIONS,
                       SITE, SITE_INFO)
from lib.store import load, rel

HEADER = "/* Собрано tools/build.py из {src}, руками не править. */\n"
ASSET = re.compile(r'((?:href|src)="((?:\.\./)?assets/(?:css|js)/[^"?]+))(?:\?v=[0-9a-f]+)?"')


def compact(obj):
    """JSON одной строкой: файл данных читает только браузер, пробелы ему не нужны."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def news_for_site(items):
    """Новости как их видит сайт: без служебных полей хранилища.
    form это номер таблицы в анкете, formTitle заголовок из анкеты до правки."""
    out = []
    for n in items:
        n = {k: v for k, v in n.items() if k not in ("form", "formTitle")}
        if not n.get("featured"):
            n.pop("featured", None)
        out.append(n)
    return out


def write_data(js, url):
    site, news = {**load(SITE_INFO), "url": url}, news_for_site(load(NEWS))
    parts = [("SITE", site), ("PEOPLE", load(PEOPLE)), ("DIRECTIONS", load(DIRECTIONS)),
             ("PUBLICATIONS", load(PUBLICATIONS)), ("NEWS", news)]
    (js / "data.js").write_text(HEADER.format(src="content/*.json")
                                + "".join(f"window.{name} = {compact(obj)};\n" for name, obj in parts),
                                encoding="utf-8", newline="\n")
    (js / "abstracts.js").write_text(HEADER.format(src=rel(ABSTRACTS))
                                     + f"window.ABSTRACTS = {compact(load(ABSTRACTS))};\n",
                                     encoding="utf-8", newline="\n")
    (js / "citations.js").write_text(HEADER.format(src=rel(CITATIONS))
                                     + f"window.CITATIONS = {compact(load(CITATIONS))};\n",
                                     encoding="utf-8", newline="\n")
    en = load(ENGLISH)
    (js / "en-content.js").write_text(HEADER.format(src=rel(ENGLISH))
                                      + "".join(f"Object.assign(window.EN.{k}, {compact(en[k])});\n"
                                                for k in ("directions", "people", "news")),
                                      encoding="utf-8", newline="\n")


def fill_placeholders(dist, url):
    path = urllib.parse.urlsplit(url).path or "/"
    for f in [*dist.glob("*.html"), dist / "robots.txt"]:
        text = f.read_text(encoding="utf-8")
        new = text.replace("{{SITE_URL}}", url).replace("{{SITE_PATH}}", path)
        if new != text:
            f.write_text(new, encoding="utf-8", newline="\n")


def sitemap(dist, url):
    """Главные страницы обеих версий и направления, у которых уже есть описание:
    остальные показывают «Описание направления готовится», в поиск им рано."""
    pages = [("", "1.0"), ("publications.html", "0.8"), ("news.html", "0.8")]
    pages += [(f"direction.html?id={d['id']}", "0.6") for d in load(DIRECTIONS) if d.get("about")]
    rows = []
    for lang, drop in (("", 0), ("en/", 0.1)):
        for page, prio in pages:
            rows.append(f"  <url>\n    <loc>{url}{lang}{page.replace('&', '&amp;')}</loc>\n"
                        f"    <priority>{float(prio) - drop:.1f}</priority>\n  </url>")
    (dist / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8", newline="\n")
    return len(rows)


def stamp(dist):
    for html in [*dist.glob("*.html"), *dist.glob("en/*.html")]:
        text = html.read_text(encoding="utf-8")
        digest = lambda m: hashlib.sha1((html.parent / m.group(2)).read_bytes()).hexdigest()[:8]
        html.write_text(ASSET.sub(lambda m: f'{m.group(1)}?v={digest(m)}"', text), encoding="utf-8", newline="\n")


def leftovers(dist):
    """Незаполненные {{...}} в готовых файлах: значит, шаблон и сборка разошлись."""
    return [f"{rel(f)}: {m}" for f in dist.rglob("*") if f.suffix in (".html", ".txt", ".xml", ".js")
            for m in set(re.findall(r"\{\{[A-Z_]+\}\}", f.read_text(encoding="utf-8")))]


def build(url=None, quiet=False):
    url = url or load(SITE_INFO)["url"]
    if not url.endswith("/"):
        url += "/"
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SITE, DIST)
    write_data(DIST / "assets" / "js", url)
    fill_placeholders(DIST, url)
    errors = english_pages.build(DIST, url)
    n = sitemap(DIST, url)
    stamp(DIST)
    errors += [f"незаполненное поле {x}" for x in leftovers(DIST)]
    if not quiet or errors:
        print(f"собрано в {rel(DIST)}/ для {url}: страниц {len([*DIST.glob('*.html'), *DIST.glob('en/*.html')])}, "
              f"в sitemap {n} адресов")
    for e in errors:
        print("  !", e)
    return not errors


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="сборка сайта в dist/")
    ap.add_argument("--url", help="адрес сайта со слешем в конце, по умолчанию из content/site.json")
    sys.exit(0 if build(ap.parse_args().url) else 1)
