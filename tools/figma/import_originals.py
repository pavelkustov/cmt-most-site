"""Сжимает оригиналы из data/figma/source-img/*-orig.* (выгрузка Figma REST API) в site/assets/img/*.webp.

Длинная сторона ограничивается по назначению картинки, короткая не меньше нужной для ретины.
"""
import pathlib
import sys

import cv2
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib.paths import FIGMA, IMG
SRC = FIGMA / "source-img"

# имя оригинала -> (имя на сайте, максимальная ширина)
TARGETS = {f"pub-{i}": (f"pub-{i}", 1200) for i in range(1, 13)}
TARGETS.update({
    "hero-publications": ("hero-publications", 2000),
    "hero-news": ("hero-news", 2000),
    "hero-direction": ("hero-direction", 2000),
})

# кадрирование как в Figma: imageTransform слоя [[sx, 0, tx], [0, sy, ty]] в долях исходника
CROPS = {
    # «Новость месяца», слой 1:2604 900x559
    "news-featured-card": ("news-featured", 1400, (0.8782845, 0.0931548, 0.3635328, 0.0972654)),
    # попап, слой 1:3112 900x990
    "news-featured-popup": ("news-featured", 1400, (0.8782845, 0.0931548, 0.6438237, 0.0877169)),
}
for dst_name, (src_name, max_w, (sx, tx, sy, ty)) in CROPS.items():
    src = next(SRC.glob(f"{src_name}-orig.*"))
    im = cv2.imdecode(np.fromfile(str(src), np.uint8), cv2.IMREAD_COLOR)
    h, w = im.shape[:2]
    im = im[round(ty * h):round((ty + sy) * h), round(tx * w):round((tx + sx) * w)]
    ch, cw = im.shape[:2]
    if cw > max_w:
        im = cv2.resize(im, (max_w, round(ch * max_w / cw)), interpolation=cv2.INTER_AREA)
    out = IMG / f"{dst_name}.webp"
    cv2.imencode(".webp", im, [cv2.IMWRITE_WEBP_QUALITY, 85])[1].tofile(str(out))
    print(f"{src.name} crop {cw}x{ch} -> {out.name} {out.stat().st_size // 1024} KB")

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
