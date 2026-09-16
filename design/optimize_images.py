"""Сжимает PNG из assets/img в WebP (исходники уезжают в design/source-img)."""
import pathlib
import shutil

import cv2
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
SRC = ROOT / "design" / "source-img"
SRC.mkdir(parents=True, exist_ok=True)

# максимальная ширина по назначению картинки
MAX_W = {"hero": 2000, "education": 1400, "industry": 900, "person": 900, "logo": 800}
DEFAULT_W = 1200

for png in sorted(IMG.glob("*.png")):
    if png.stem == "logo":
        continue  # логотип оставляем PNG
    data = np.fromfile(str(png), dtype=np.uint8)
    im = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
    limit = next((w for k, w in MAX_W.items() if png.stem.startswith(k)), DEFAULT_W)
    h, w = im.shape[:2]
    if w > limit:
        im = cv2.resize(im, (limit, round(h * limit / w)), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".webp", im, [cv2.IMWRITE_WEBP_QUALITY, 82])
    assert ok, png
    out = png.with_suffix(".webp")
    buf.tofile(str(out))
    shutil.move(str(png), SRC / png.name)
    print(f"{png.name}: {w}x{h} -> {out.name} {out.stat().st_size // 1024} KB")
