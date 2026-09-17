"""Рисует картинки для превью ссылок (og:image) и PNG-иконки сайта.

assets/og/<страница>.jpg   1200x630, превью в Telegram, VK, соцсетях
assets/icons/favicon-32.png, apple-touch-icon.png   запасные иконки к favicon.svg
Запуск: python tools/make_share_images.py   (нужен playwright и доступ к Google Fonts)
"""
import base64
import pathlib
import re
from playwright.sync_api import sync_playwright

# то же правило, что в layout.js: предлоги и короткие союзы не висят в конце строки
HANGING = r"в|во|без|до|из|изо|к|ко|на|над|надо|о|об|обо|от|ото|по|под|подо|при|про|с|со|у|через|для|за|перед|между|и|а|но|да|или|ни|не"
nbsp = lambda s: re.sub(rf"(?<![^\W\d_])({HANGING}) (?=\S)", "\\1\u00a0", s, flags=re.I)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OG = ROOT / "assets" / "og"
ICONS = ROOT / "assets" / "icons"

# мост из логотипа (перерисован в вектор по logo.png), координаты в поле 156x154
BRIDGE = ('<path d="M31 41C36 70 55 85 78 85S120 70 125 41"/>'
          '<path d="M31 41C37 66 38 92 26 111M125 41C119 66 118 92 130 111"/>'
          '<path d="M26 111C45 92 60 88 78 88S111 92 130 111"/>'
          '<path d="M41 76 54.5 114M116 76 101 114"/>')

PAGES = {
    "home": ("<em>Соединяем</em><br>образование,<br>науку и индустрию", "Научные идеи доводим до практических R&amp;D-решений и интегрируем в образование", "hero-home.webp"),
    "publications": ("<em>Публикации</em><br>ЦМТ «Мост»", "Статьи в рецензируемых журналах, труды конференций и патенты", "hero-publications.webp"),
    "news": ("<em>Новости</em><br>ЦМТ «Мост»", "Конференции, награды, гранты и новые проекты центра", "hero-news.webp"),
    "direction": ("<em>Научные</em><br>направления", "Команды, исследования и публикации ЦМТ «Мост»", "hero-direction.webp"),
}


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def card_html(title, sub, bg):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;1,300&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; box-sizing: border-box; }}
  body {{ width: 1200px; height: 630px; overflow: hidden; font-family: Inter, Arial, sans-serif; color: #f2fdfb; background: #0d1a14; }}
  .bg {{ position: absolute; inset: -20px; background: url({data_uri(ROOT / "assets" / "img" / bg, "image/webp")}) center / cover; filter: blur(6px) brightness(.8); }}
  .shade {{ position: absolute; inset: 0; background: linear-gradient(62deg, rgba(9,9,11,.78) 30%, rgba(9,9,11,.15) 100%); }}
  .wrap {{ position: absolute; inset: 56px 64px; display: flex; flex-direction: column; justify-content: space-between; }}
  .logo {{ width: 330px; }}
  h1 {{ font-size: 76px; font-weight: 400; line-height: 1; letter-spacing: -.02em; }}
  h1 em {{ font-style: italic; font-weight: 300; }}
  .sub {{ margin-top: 26px; font-size: 28px; font-weight: 300; line-height: 1.35; max-width: 800px; opacity: .9; }}
  .foot {{ display: flex; justify-content: space-between; align-items: center; font-size: 22px; font-weight: 500; letter-spacing: .02em; }}
  .url {{ padding: 12px 20px; border-radius: 14px; background: rgba(242,253,251,.16); backdrop-filter: blur(8px); }}
  .itmo {{ opacity: .75; font-weight: 400; }}
</style></head><body>
<div class="bg"></div><div class="shade"></div>
<div class="wrap">
  <img class="logo" src="{data_uri(ROOT / "assets" / "img" / "logo.png", "image/png")}" alt="">
  <div><h1>{nbsp(title)}</h1><p class="sub">{nbsp(sub)}</p></div>
  <div class="foot"><span class="url">pavelkustov.github.io/cmt-most-site</span><span class="itmo">Университет ИТМО · физический факультет</span></div>
</div></body></html>"""


def icon_html(size):
    return f"""<!doctype html><html><body style="margin:0;background:transparent">
<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 64 64">
<rect width="64" height="64" rx="{0 if size >= 180 else 14}" fill="#3F8259"/>
<g transform="translate(-3.9 -3.65) scale(.46)" fill="none" stroke="#F2FDFB" stroke-width="9" stroke-linecap="round">{BRIDGE}</g></svg>
</body></html>"""


def main():
    OG.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 630})
        for name, (title, sub, bg) in PAGES.items():
            pg.set_content(card_html(title, sub, bg), wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(OG / f"{name}.jpg"), type="jpeg", quality=88)
            print("готово", f"assets/og/{name}.jpg")
        for size, file in [(32, "favicon-32.png"), (180, "apple-touch-icon.png")]:
            ip = b.new_page(viewport={"width": size, "height": size})
            ip.set_content(icon_html(size))
            ip.screenshot(path=str(ICONS / file), omit_background=True)
            ip.close()
            print("готово", f"assets/icons/{file}")
        b.close()


main()
