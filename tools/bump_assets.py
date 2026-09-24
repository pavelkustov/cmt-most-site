"""Проставляет в HTML ссылки на CSS/JS с меткой версии ?v=<хэш содержимого>.

GitHub Pages отдает файлы с max-age=600, и без метки браузер до 10 минут показывает старые стили.
Запускать перед коммитом: python tools/bump_assets.py
"""
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
# английские страницы лежат в en/ и ссылаются на ../assets
ASSET = re.compile(r'((?:href|src)="((?:\.\./)?assets/(?:css|js)/[^"?]+))(?:\?v=[0-9a-f]+)?"')

changed = 0
for html in sorted([*ROOT.glob("*.html"), *ROOT.glob("en/*.html")]):
    text = html.read_text(encoding="utf-8")

    def repl(m):
        digest = hashlib.sha1((html.parent / m.group(2)).read_bytes()).hexdigest()[:8]
        return f'{m.group(1)}?v={digest}"'

    new = ASSET.sub(repl, text)
    if new != text:
        html.write_text(new, encoding="utf-8", newline="\n")
        changed += 1
        print("обновлен", html.relative_to(ROOT).as_posix())
print(f"готово, файлов изменено: {changed}")
