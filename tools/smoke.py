"""Смоук-проверка сайта: ошибки JS, битые картинки, горизонтальный скролл, базовые сценарии.

Запуск из корня проекта:
    python tools/smoke.py            # поднимет локальный сервер сам
    python tools/smoke.py --shots    # плюс скриншоты в tools/shots/
"""
import http.server
import pathlib
import socketserver
import sys
import threading
from functools import partial

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOTS = "--shots" in sys.argv
PAGES = ["index.html", "direction.html?id=puf", "direction.html?id=biosensing", "publications.html", "news.html"]
WIDTHS = [1920, 1440, 1024, 390]

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


handler = partial(QuietHandler, directory=str(ROOT))
httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
port = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{port}/"
# --base https://pavelkustov.github.io/cmt-most-site/ проверяет опубликованный сайт
if "--base" in sys.argv:
    base = sys.argv[sys.argv.index("--base") + 1].rstrip("/") + "/"
# живой сайт бывает медленным (GitHub Pages из РФ), там ждем событие load с большим таймаутом
WAIT = "load" if "--base" in sys.argv else "networkidle"
TIMEOUT = 120_000 if "--base" in sys.argv else 30_000

problems = []
checks = 0


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        problems.append(msg)


with sync_playwright() as p:
    browser = p.chromium.launch()
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
            page.goto(base + url, wait_until=WAIT, timeout=TIMEOUT)
            tag = f"[{width}] {url}"
            check(not errors, f"{tag}: ошибки JS {errors}")
            check(not bad, f"{tag}: битые ресурсы {bad}")
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check(overflow <= 1, f"{tag}: горизонтальный скролл страницы {overflow}px")
            broken = page.evaluate("""[...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.loading !== 'lazy').map(i => i.src)""")
            check(not broken, f"{tag}: не загрузились картинки {broken}")
            check(page.locator(".site-header").count() == 1, f"{tag}: нет шапки")
            check(page.locator(".site-footer").count() == 1, f"{tag}: нет подвала")
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
    check(page.locator(".dir-card").count() == 10, "главная: должно быть 10 карточек направлений")
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
    check(page.locator(".pub").count() == 1, "публикации: поиск по журналу не сработал")
    page.click(".filters__reset")
    page.select_option("[name=year]", "2022")
    check(page.locator(".pub").count() == 4, f"публикации: фильтр по году дал {page.locator('.pub').count()}")
    page.click(".view-toggle__btn[data-view=list]")
    check(page.locator(".pub-list.is-list").count() == 1, "публикации: не переключился вид «список»")
    check(not page.locator(".pub__img").first.is_visible(), "публикации: в виде «список» видны картинки")

    page.goto(base + "news.html", wait_until=WAIT, timeout=TIMEOUT)
    page.click(".featured__card")
    check(page.locator(".modal").is_visible(), "новости: попап не открылся")
    page.keyboard.press("Escape")
    check(not page.locator(".modal").is_visible(), "новости: попап не закрылся по Esc")
    page.goto(base + "news.html?open=news-2", wait_until=WAIT, timeout=TIMEOUT)
    check(page.locator(".modal").is_visible(), "новости: попап по ссылке ?open= не открылся")

    # первый экран целиком помещается в широкие невысокие окна (Chrome с панелями, масштаб Windows 125%)
    fits = [(w, h, u) for w, h in [(2000, 930), (1536, 730), (1920, 960), (2560, 1300)]
            for u in ["index.html", "direction.html?id=puf", "news.html"]]
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
            return {top: top - header.bottom, bottom: hero.bottom - bottom};
        })()""")
        check(abs(gaps["top"] - gaps["bottom"]) <= 3, f"[{w}x{h}] {u}: отступы сверху и снизу разные: {gaps}")
        if SHOTS:
            pg.screenshot(path=str(ROOT / "tools" / "shots" / f"fit-{w}x{h}-{u.split('.')[0]}.png"))
        pg.close()

    mob = browser.new_context(viewport={"width": 390, "height": 844}).new_page()
    mob.goto(base + "index.html", wait_until=WAIT, timeout=TIMEOUT)
    check(not mob.locator(".nav").is_visible(), "мобилка: меню видно до нажатия бургера")
    mob.click(".burger")
    check(mob.locator(".nav").is_visible(), "мобилка: бургер не открыл меню")
    browser.close()

httpd.shutdown()
print(f"проверок {checks}, проблем {len(problems)}")
for pr in problems:
    print(" -", pr)
sys.exit(1 if problems else 0)
