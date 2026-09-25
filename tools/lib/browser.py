"""Браузер для проверок и замеров (смоук, заголовки новостей, картинки превью)."""


def launch(pw):
    """Chromium из Playwright, а если его нет, установленный Microsoft Edge или Google Chrome.
    Движок у всех один, Chromium. Запасной путь нужен потому, что сервер загрузки браузеров
    Playwright из России часто недоступен, а Edge есть на любом Windows 10 и 11."""
    for kw in ({}, {"channel": "msedge"}, {"channel": "chrome"}):
        try:
            return pw.chromium.launch(**kw)
        except Exception:
            continue
    raise SystemExit("нет браузера: python -m playwright install chromium, или установите Microsoft Edge или Google Chrome")
