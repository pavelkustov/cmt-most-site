# Исходники макета из Figma

Локальная папка, в git уходит только этот README.

- `source-img/` оригиналы картинок, выгруженные из Figma (десятки мегабайт). Из них
  `tools/figma/import_originals.py` делает сжатые WebP в `site/assets/img`.
- `assets_manifest.txt` список ссылок на ассеты Figma для `tools/figma/download.py`
  (ссылки Figma живут около недели).
- `render-*.png` рендеры страниц макета для сверки верстки.

Сайт от этой папки не зависит: все, что нужно странице, уже лежит в `site/assets`.
