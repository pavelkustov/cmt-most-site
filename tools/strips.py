"""Режет мобильные full-page скриншоты на колонки, чтобы их было удобно смотреть целиком."""
import pathlib

import cv2
import numpy as np

d = pathlib.Path(__file__).resolve().parent / "shots"
out = d / "mobile"
out.mkdir(exist_ok=True)
H = 1700
for f in sorted(d.glob("390-*.png")):
    im = cv2.imdecode(np.fromfile(str(f), np.uint8), cv2.IMREAD_COLOR)
    h, w = im.shape[:2]
    cols = [im[y:y + H] for y in range(0, h, H)]
    for k in range(0, len(cols), 4):
        group = cols[k:k + 4]
        canvas = np.full((H, (w + 20) * len(group), 3), 120, np.uint8)
        for i, c in enumerate(group):
            canvas[:c.shape[0], i * (w + 20):i * (w + 20) + w] = c
        cv2.imencode(".jpg", canvas, [cv2.IMWRITE_JPEG_QUALITY, 80])[1].tofile(str(out / f"{f.stem}__{k // 4}.jpg"))
        print(f"{f.stem}__{k // 4}.jpg")
