"""Складывает шрифты Inter и Roboto в site/assets/fonts и собирает site/assets/css/fonts.css.

Сайт не должен зависеть от fonts.googleapis.com: из России оттуда медленно, а иногда и вовсе
недоступно (из-за этого падал смоук). Скрипт берет у Google тот же набор начертаний, что был
подключен ссылкой, скачивает файлы woff2 в assets/fonts и переписывает пути на локальные.

Запуск: python tools/assets/fonts.py
В имени файла хэш содержимого, поэтому ссылки rel="preload" в head страниц скрипт
переписывает сам.
"""
import hashlib
import pathlib
import re
import sys
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
# ровно тот набор, что был в ссылке на Google Fonts
CSS_URL = ("https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300"
           "&family=Roboto:wght@300;400;600&display=swap")
# подмножества: кириллица и латиница, остальные алфавиты сайту не нужны
KEEP = {"cyrillic", "cyrillic-ext", "latin", "latin-ext"}

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib.paths import SITE

FONTS = SITE / "assets" / "fonts"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    FONTS.mkdir(parents=True, exist_ok=True)
    for old in FONTS.glob("*.woff2"):
        old.unlink()

    # современному браузеру Google отдает woff2, по одному переменному файлу на подмножество и начертание
    css = get(CSS_URL).decode("utf-8")
    blocks = re.findall(r"/\* ([\w-]+) \*/\s*(@font-face \{.*?\})", css, re.S)

    names, out = {}, []
    for subset, block in blocks:
        if subset not in KEEP:
            continue
        url = re.search(r"url\((https://[^)]+)\)", block).group(1)
        if url not in names:
            data = get(url)
            family = re.search(r"font-family: '([^']+)'", block).group(1).lower()
            italic = "-italic" if "font-style: italic" in block else ""
            digest = hashlib.sha1(data).hexdigest()[:8]
            name = f"{family}-{subset}{italic}-{digest}.woff2"
            (FONTS / name).write_bytes(data)
            names[url] = name
            print(f"{name:<44} {len(data) / 1024:6.1f} КБ")
        out.append(f"/* {subset} */\n" + block.replace(f"url({url})", f"url(../fonts/{names[url]})"))

    header = (
        "/* Шрифты Inter и Roboto лежат в репозитории (assets/fonts), а не грузятся с Google Fonts:\n"
        "   из России так быстрее и сайт не зависит от внешнего сервиса.\n"
        "   Файл собран скриптом tools/assets/fonts.py, подмножества латиница и кириллица.\n"
        "   Обновить: python tools/assets/fonts.py */\n\n"
    )
    (SITE / "assets" / "css" / "fonts.css").write_text(header + "\n\n".join(out) + "\n", encoding="utf-8", newline="\n")
    # предзагрузка шрифтов в head страниц ссылается на имя с хэшем: переписываем на новые имена
    fresh = {name.rsplit("-", 1)[0]: name for name in names.values()}
    for html in SITE.glob("*.html"):
        text = html.read_text(encoding="utf-8")
        new = re.sub(r"assets/fonts/([a-z-]+)-[0-9a-f]{8}\.woff2",
                     lambda m: "assets/fonts/" + fresh.get(m.group(1), m.group(0).split("/")[-1]), text)
        if new != text:
            html.write_text(new, encoding="utf-8", newline="\n")
            print("предзагрузка обновлена:", html.name)
    total = sum(f.stat().st_size for f in FONTS.glob("*.woff2"))
    print(f"файлов {len(names)}, всего {total / 1024:.0f} КБ")


if __name__ == "__main__":
    main()
