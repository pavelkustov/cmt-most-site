"""Склеивает верх нескольких страниц в одну картинку для быстрой сверки первых экранов."""
import pathlib

import cv2
import numpy as np

d = pathlib.Path(__file__).resolve().parent / "shots"
names = ["1920-index.html", "1440-publications.html", "1920-direction.html_id-puf", "1024-news.html"]
tiles = []
for name in names:
    im = cv2.imdecode(np.fromfile(str(d / f"{name}.png"), np.uint8), cv2.IMREAD_COLOR)
    w = im.shape[1]
    c = im[: int(w * 0.62)]
    tiles.append(cv2.resize(c, (800, int(c.shape[0] * 800 / w)), interpolation=cv2.INTER_AREA))
H = max(t.shape[0] for t in tiles)
canvas = np.full((H * 2 + 10, 1610, 3), 120, np.uint8)
for i, t in enumerate(tiles):
    y, x = (i // 2) * (H + 10), (i % 2) * 810
    canvas[y:y + t.shape[0], x:x + 800] = t
out = d / "heroes.jpg"
cv2.imencode(".jpg", canvas, [cv2.IMWRITE_JPEG_QUALITY, 82])[1].tofile(str(out))
print(out)
