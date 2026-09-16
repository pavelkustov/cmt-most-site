"""Сжимает оригиналы из design/source-img/*-orig.* (выгрузка Figma REST API) в assets/img/*.webp.

Длинная сторона ограничивается по назначению картинки, короткая не меньше нужной для ретины.
"""
import pathlib

import cv2
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "design" / "source-img"
IMG = ROOT / "assets" / "img"

# имя оригинала -> (имя на сайте, максимальная ширина)
TARGETS = {f"pub-{i}": (f"pub-{i}", 1200) for i in range(1, 13)}
TARGETS.update({
    "hero-publications": ("hero-publications", 2000),
    "hero-news": ("hero-news", 2000),
    "hero-direction": ("hero-direction", 2000),
    "news-featured": ("news-featured", 1400),
    "person-eco-2": ("person-yali-sun", 1600),
})

for src_name, (dst_name, max_w) in TARGETS.items():
    src = next(SRC.glob(f"{src_name}-orig.*"))
    im = cv2.imdecode(np.fromfile(str(src), np.uint8), cv2.IMREAD_COLOR)
    h, w = im.shape[:2]
    if w > max_w:
        im = cv2.resize(im, (max_w, round(h * max_w / w)), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".webp", im, [cv2.IMWRITE_WEBP_QUALITY, 82])
    assert ok, src
    out = IMG / f"{dst_name}.webp"
    buf.tofile(str(out))
    print(f"{src.name} {w}x{h} -> {out.name} {out.stat().st_size // 1024} KB")
