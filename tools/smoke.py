"""Смоук-проверка сайта: ошибки JS, битые картинки, горизонтальный скролл, базовые сценарии.

Запуск из корня проекта:
    python tools/smoke.py            # поднимет локальный сервер сам
    python tools/smoke.py --shots    # плюс скриншоты в tools/shots/
"""
import http.server
import re
import pathlib
import socketserver
import sys
import threading
from functools import partial

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOTS = "--shots" in sys.argv
PAGES = ["index.html", "direction.html?id=puf", "direction.html?id=biosensing", "publications.html", "news.html", "404.html",
         # английская версия: страницы собирает tools/build_en.py
         "en/index.html", "en/direction.html?id=puf", "en/publications.html", "en/news.html"]
WIDTHS = [1920, 1440, 1024, 390]

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def handle_one_request(self):
        # браузер бросает лишние соединения (предзагрузка шрифтов), на Windows это ошибка в консоли
        try:
            super().handle_one_request()
        except (ConnectionAbortedError, ConnectionResetError):
            self.close_connection = True


# сервер многопоточный: браузер открывает несколько соединений сразу, на одном потоке страница зависала
class QuietServer(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


handler = partial(QuietHandler, directory=str(ROOT))
httpd = QuietServer(("127.0.0.1", 0), handler)
port = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{port}/"
# --base https://pavelkustov.github.io/cmt-most-site/ проверяет опубликованный сайт
if "--base" in sys.argv:
    base = sys.argv[sys.argv.index("--base") + 1].rstrip("/") + "/"
# живой сайт бывает медленным (GitHub Pages из РФ), там ждем событие load с большим таймаутом
WAIT = "load"  # networkidle зависает, когда тормозят внешние шрифты
TIMEOUT = 120_000 if "--base" in sys.argv else 30_000

problems = []
notes = []
checks = 0

# ожидания считаем по данным сайта, а не пишем числом: контент меняется часто
_data = (ROOT / "assets" / "js" / "data.js").read_text(encoding="utf-8")
_dirs_block = _data[:_data.index("window.PUBLICATIONS")]
_pubs_block = _data[_data.index("window.PUBLICATIONS"):_data.index("window.NEWS")]
_news_block = _data[_data.index("window.NEWS"):]
N_DIRECTIONS = len(re.findall(r'id: "[^"]+"', _dirs_block))
N_PUBS_2022 = _pubs_block.count('date: "2022')
PUB_PAGE = 6  # столько публикаций показывает страница до кнопки «показать еще»
# поиск на странице публикаций идет по названию, авторам, журналу и тегам
_pub_blocks = re.findall(r"\n  \{\n    date:.*?\n  \},", _pubs_block, re.S)
N_NATURE = sum(1 for b in _pub_blocks if "nature" in b.lower())
NEWS_IDS = re.findall(r'id: "([^"]+)"', _news_block)
N_NEWS = len(NEWS_IDS)
NEWS_PAGE = 6  # столько новостей показывает страница до кнопки «показать еще», кроме новости месяца

# метки версий CSS/JS в HTML должны совпадать с содержимым файлов, иначе браузеры покажут старый кэш
import hashlib

stale = []
for html in [*ROOT.glob("*.html"), *ROOT.glob("en/*.html")]:
    for path, ver in re.findall(r'(?:href|src)="((?:\.\./)?assets/(?:css|js)/[^"?]+)(?:\?v=([0-9a-f]+))?"', html.read_text(encoding="utf-8")):
        if ver != hashlib.sha1((html.parent / path).read_bytes()).hexdigest()[:8]:
            stale.append(f"{html.relative_to(ROOT).as_posix()}: {path}")


def note(cond, msg):
    """Замечание по содержимому: гейт не валит, но печатается в конце.

    Заголовки и анонсы пишет владелец, и слишком длинный текст это не поломка верстки,
    а повод подрезать текст, поэтому такие вещи идут отдельным списком.
    """
    if not cond:
        notes.append(msg)


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        problems.append(msg)


check(not stale, f"устаревшие метки версий, запустите python tools/bump_assets.py: {stale}")


with sync_playwright() as p:
    browser = p.chromium.launch()
    # раскладку проверяем без анимации появления первого экрана, иначе замеры попадают на середину движения
    browser.new_context = (lambda orig: lambda **kw: orig(**{"reduced_motion": "reduce", **kw}))(browser.new_context)
    for width in WIDTHS:
        ctx = browser.new_context(viewport={"width": width, "height": 900})
        for url in PAGES:
            page = ctx.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            # DNS-сбои внешних шрифтов (VPN, сеть) не считаем ошибкой сайта
            page.on("console", lambda m: m.type == "error" and "ERR_NAME_NOT_RESOLVED" not in m.text and errors.append(m.text))
            bad = []
            page.on("response", lambda r: r.status >= 400 and "fonts." not in r.url and bad.append(f"{r.status} {r.url}"))
            # шрифты лежат в репозитории, обращений к Google Fonts быть не должно
            external = []
            page.on("request", lambda r: ("fonts.googleapis.com" in r.url or "fonts.gstatic.com" in r.url) and external.append(r.url))
            page.goto(base + url, wait_until=WAIT, timeout=TIMEOUT)
            tag = f"[{width}] {url}"
            check(not errors, f"{tag}: ошибки JS {errors}")
            check(not bad, f"{tag}: битые ресурсы {bad}")
            check(not external, f"{tag}: страница ходит за шрифтами наружу {external}")
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check(overflow <= 1, f"{tag}: горизонтальный скролл страницы {overflow}px")
            broken = page.evaluate("""[...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.loading !== 'lazy').map(i => i.src)""")
            check(not broken, f"{tag}: не загрузились картинки {broken}")
            if url != "404.html":  # страница «не найдено» идет без шапки и подвала
                check(page.locator(".site-header").count() == 1, f"{tag}: нет шапки")
                check(page.locator(".site-footer").count() == 1, f"{tag}: нет подвала")
            else:
                check(page.locator(".oops__logo").count() == 1, f"{tag}: нет логотипа")
            if SHOTS:
                out = ROOT / "tools" / "shots" / f"{width}-{url.replace('?', '_').replace('=', '-')}.png"
                out.parent.mkdir(exist_ok=True)
                page.screenshot(path=str(out), full_page=True)
            page.close()
        ctx.close()

    # сценарии на десктопе
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.goto(base + "index.html", wait_until=WAIT, timeout=TIMEOUT)
    check(page.locator(".dir-card").count() == N_DIRECTIONS, f"главная: карточек направлений {page.locator('.dir-card').count()}, в data.js {N_DIRECTIONS}")
    check(page.locator(".news__grid .news-card").count() == 3, "главная: должно быть 3 новости")
    page.click(".nav__item[aria-controls='nav-science']")
    check(page.locator("#nav-science").is_visible(), "меню «Наука» не раскрылось")
    prev = page.locator(".slider-arrows .square-btn").first
    check(prev.is_disabled(), "стрелка «назад» карусели должна быть неактивна в начале")
    page.locator(".slider-arrows .square-btn").last.click()
    page.wait_for_timeout(700)
    check(not prev.is_disabled(), "карусель не прокрутилась")

    page.goto(base + "publications.html", wait_until=WAIT, timeout=TIMEOUT)
    check(page.locator(".pub").count() == 6, "публикации: на первой странице должно быть 6")
    page.click(".more .btn")
    check(page.locator(".pub").count() == 12, "публикации: «показать еще» не догрузил")
    page.fill("[name=q]", "Nature")
    want = min(N_NATURE, PUB_PAGE)
    check(page.locator(".pub").count() == want,
          f"публикации: поиск дал {page.locator('.pub').count()}, ждали {want}")
    page.click(".filters__reset")
    page.select_option("[name=year]", "2022")
    want = min(N_PUBS_2022, PUB_PAGE)
    check(page.locator(".pub").count() == want,
          f"публикации: фильтр по году дал {page.locator('.pub').count()}, ждали {want} (в data.js {N_PUBS_2022})")
    page.click(".view-toggle__btn[data-view=list]")
    check(page.locator(".pub-list.is-list").count() == 1, "публикации: не переключился вид «список»")
    check(not page.locator(".pub__img").first.is_visible(), "публикации: в виде «список» видны картинки")

    page.goto(base + "news.html", wait_until=WAIT, timeout=TIMEOUT)
    check(str(N_NEWS) in page.locator(".news-all .pubs__sub").inner_text(),
          f"новости: в подписи нет числа новостей из data.js ({N_NEWS})")
    check(page.locator(".news-all .news-card").count() == min(NEWS_PAGE, N_NEWS - 1),
          f"новости: на первой странице {page.locator('.news-all .news-card').count()}, ждали {min(NEWS_PAGE, N_NEWS - 1)}")
    page.click(".news-all .more .btn")
    check(page.locator(".news-all .news-card").count() == min(2 * NEWS_PAGE, N_NEWS - 1),
          "новости: «показать еще» не догрузил")
    # заголовки переписаны под три строки: обрезанных многоточием быть не должно
    cut = page.eval_on_selector_all(
        ".news-all .news-card__title, .featured__title",
        "els => els.filter(e => e.scrollHeight > e.clientHeight + 1).map(e => e.textContent.slice(0, 40))")
    note(not cut, f"новости: заголовок не встал в три строки, обрезан многоточием: {cut}")
    # карточки в ряду одинаковые: ссылка «читать» у всех на одной линии от верха карточки
    tops = page.eval_on_selector_all(
        ".news-all .news-card",
        "els => els.map(e => Math.round(e.querySelector('.link-arrow').getBoundingClientRect().top"
        " - e.getBoundingClientRect().top))")
    check(len(set(tops)) == 1, f"новости: «читать» в карточках на разной высоте: {sorted(set(tops))}")
    page.click(".featured__card")
    check(page.locator(".modal").is_visible(), "новости: попап не открылся")
    page.keyboard.press("Escape")
    check(not page.locator(".modal").is_visible(), "новости: попап не закрылся по Esc")
    # id берем из data.js: заглушки из макета убраны, а имена новостей меняются вместе с контентом
    page.goto(base + f"news.html?open={NEWS_IDS[1]}", wait_until=WAIT, timeout=TIMEOUT)
    check(page.locator(".modal").is_visible(), "новости: попап по ссылке ?open= не открылся")
    check(bool(page.locator(".modal__title").inner_text().strip()),
          "новости: в попапе пустой заголовок")

    # первый экран целиком помещается в широкие невысокие окна (Chrome с панелями, масштаб Windows 125%)
    fits = [(w, h, u) for w, h in [(2000, 930), (1536, 730), (1920, 960), (2560, 1300)]
            for u in ["index.html", "direction.html?id=puf", "news.html", "en/index.html", "en/direction.html?id=puf", "en/news.html"]]
    for w, h, u in fits:
        pg = browser.new_context(viewport={"width": w, "height": h}).new_page()
        pg.goto(base + u, wait_until=WAIT, timeout=TIMEOUT)
        box = pg.evaluate("""(() => {
            const hero = document.querySelector('.hero').getBoundingClientRect();
            const btn = (document.querySelector('.hero .btn') || document.querySelector('.hero__subtitle')).getBoundingClientRect();
            const title = document.querySelector('.hero__title').getBoundingClientRect();
            const header = document.querySelector('.site-header').getBoundingClientRect();
            const nav = document.querySelector('.nav__bar').getBoundingClientRect();
            return {heroBottom: hero.bottom, btnBottom: btn.bottom, titleLeft: title.left, navRight: nav.right, titleTop: (document.querySelector('.hero__back') || document.querySelector('.hero__title')).getBoundingClientRect().top, headerBottom: header.bottom};
        })()""")
        check(box["heroBottom"] <= h + 1, f"[{w}x{h}] {u}: первый экран не помещается: {box}")
        check(box["btnBottom"] <= h, f"[{w}x{h}] {u}: низ первого экрана за краем окна: {box}")
        check(box["titleTop"] >= box["headerBottom"] + 20, f"[{w}x{h}] {u}: заголовок налезает на шапку: {box}")
        gaps = pg.evaluate("""(() => {
            const hero = document.querySelector('.hero').getBoundingClientRect();
            const header = document.querySelector('.site-header').getBoundingClientRect();
            const content = [...document.querySelector('.hero__content').querySelectorAll('.hero__back, .hero__title, .hero__subtitle, .hero .btn')]
                .map(e => e.getBoundingClientRect());
            const top = Math.min(...content.map(r => r.top)), bottom = Math.max(...content.map(r => r.bottom));
            return {top: header.top - hero.top, bottom: hero.bottom - bottom};
        })()""")
        # с 2026-09-17: над шапкой 4rem (как sohub.digital), под кнопкой 8rem — нижнее поле вдвое больше верхнего
        check(abs(gaps["bottom"] - 2 * gaps["top"]) <= 3, f"[{w}x{h}] {u}: поле под кнопкой не вдвое больше поля над шапкой: {gaps}")
        if SHOTS:
            pg.screenshot(path=str(ROOT / "tools" / "shots" / f"fit-{w}x{h}-{u.split('.')[0]}.png"))
        pg.close()

    # страница «не найдено» помещается в окно целиком, прокрутки быть не должно
    for w, h in [(2000, 930), (1536, 730), (1920, 1080), (1366, 640), (390, 844)]:
        pg = browser.new_context(viewport={"width": w, "height": h}).new_page()
        pg.goto(base + "404.html", wait_until=WAIT, timeout=TIMEOUT)
        over = pg.evaluate("document.documentElement.scrollHeight - document.documentElement.clientHeight")
        check(over <= 1, f"[{w}x{h}] 404: страница не помещается в окно, лишние {over}px")
        if SHOTS:
            pg.screenshot(path=str(ROOT / "tools" / "shots" / f"404-{w}x{h}.png"))
        pg.close()

    # попап целиком виден в окне, а длинный текст прокручивается внутри него.
    # Раньше проверялось, что текст влезает без прокрутки, и это скрывало обрезку:
    # тело попапа росло выше окна, а край окна отрезал последние абзацы
    for w, h in [(2000, 930), (1536, 730), (1920, 1080), (1440, 900)]:
        pg = browser.new_context(viewport={"width": w, "height": h}).new_page()
        pg.goto(base + "news.html?open=kustov-phd", wait_until=WAIT, timeout=TIMEOUT)
        pg.wait_for_timeout(400)
        m = pg.evaluate("""(() => {
            const d = document.querySelector('.modal__dialog').getBoundingClientRect();
            const b = document.querySelector('.modal__body');
            return {top: d.top, bottom: d.bottom, overflow: b.scrollHeight - b.clientHeight};
        })()""")
        check(m["top"] >= 0 and m["bottom"] <= h, f"[{w}x{h}] попап выходит за окно: {m}")
        end = pg.evaluate("""(() => {
            const b = document.querySelector('.modal__body');
            b.scrollTop = b.scrollHeight;
            b.dispatchEvent(new Event('scroll'));
            const d = document.querySelector('.modal__dialog');
            return {left: b.scrollHeight - b.clientHeight - b.scrollTop,
                    hint: d.classList.contains('at-end')};
        })()""")
        check(end["left"] <= 2, f"[{w}x{h}] текст попапа не прокручивается до конца: {end}")
        check(end["hint"], f"[{w}x{h}] подсказка о прокрутке не гаснет в конце текста: {end}")
        if SHOTS:
            pg.screenshot(path=str(ROOT / "tools" / "shots" / f"popup-{w}x{h}.png"))
        pg.close()

    # английская версия: язык страницы, переключатель ведет на ту же страницу другого языка, логотип свой.
    # Кириллица в тексте страницы пока не ошибка (направления и новости переводятся по этапам), а замечание
    en = browser.new_context(viewport={"width": 1440, "height": 900}).new_page()
    for u in ["index.html", "news.html", "publications.html", "direction.html?id=puf"]:
        en.goto(base + "en/" + u, wait_until=WAIT, timeout=TIMEOUT)
        check(en.evaluate("document.documentElement.lang") == "en", f"en/{u}: у страницы не английский lang")
        href = en.locator("[data-lang-switch]").get_attribute("href") or ""
        check(href.startswith("../") and u.split("?")[0] in href, f"en/{u}: переключатель ведет не на русскую версию: {href}")
        check("logo-en" in (en.locator(".site-header__logo img").get_attribute("src") or ""), f"en/{u}: в шапке не английский логотип")
        # русским намеренно остается помеченное lang="ru" (кнопка «Ру», двуязычное название программы)
    # и список публикаций: названия, абстракты и теги работ на языке статьи
        ru_left = en.evaluate("""(() => { const c = document.body.cloneNode(true); c.querySelectorAll('[lang=ru], .pub-list').forEach((e) => e.remove());
            document.body.append(c); c.style.cssText = 'position:absolute;left:-99999px'; const n = (c.innerText.match(/[А-Яа-яЁё]+/g) || []).length; c.remove(); return n; })()""")
        note(ru_left == 0, f"en/{u}: на странице {ru_left} русских слов, не хватает перевода (docs/EN_VERSION.md)")
    en.goto(base + "index.html", wait_until=WAIT, timeout=TIMEOUT)
    href = en.locator("[data-lang-switch]").get_attribute("href") or ""
    check(href.startswith("en/"), f"главная: переключатель EN ведет не в en/: {href}")
    en.close()

    mob = browser.new_context(viewport={"width": 390, "height": 844}).new_page()
    mob.goto(base + "index.html", wait_until=WAIT, timeout=TIMEOUT)
    check(not mob.locator(".nav").is_visible(), "мобилка: меню видно до нажатия бургера")
    mob.click(".burger")
    check(mob.locator(".nav").is_visible(), "мобилка: бургер не открыл меню")
    browser.close()

httpd.shutdown()
print(f"проверок {checks}, проблем {len(problems)}")
for n in notes:
    print(" ~ " + n)
for pr in problems:
    print(" -", pr)
sys.exit(1 if problems else 0)
