"""Переносит фотографии новостей из папки «Фото» рядом с репозиторием в assets/img.

Владелец складывает снимки под номером новости из анкеты: 1.jpg — новость 1, 7.png — седьмая.
Из каждого снимка делается два кадра, потому что места на странице разные:

- карточка и новость месяца: 3:2, файл news-<имя новости>.webp;
- окно новости: колонка почти квадратная, файл news-<имя новости>-popup.webp.

Кадр выбирается по лицам (каскад OpenCV): все найденные лица попадают внутрь, а их центр
встает в верхнюю треть кадра, поэтому люди не обрезаются по макушку и по пояс. Если лиц
не нашлось, кадр берется по центру и чуть выше середины.

Оригиналы в репозиторий не кладем, на сайт идет только сжатая копия.

Запуск: python tools/news_photos.py [--dry] [--src ПУТЬ]
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

import cv2
import numpy as np
from PIL import Image, ImageOps

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from news_from_form import STORE, write_js, write_store  # разбор анкеты живет там
from sources import PHOTOS as SRC  # снимки лежат в data/photos, путь ведет общий модуль

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
# ширина и соотношение сторон для двух мест на странице. Числа из макета:
# карточка 520x330 и новость месяца 900x559 это 3:2, колонка окна новости 900x990
SIZES = {"": (1600, 3 / 2), "-popup": (1100, 900 / 990)}
QUALITY = 80
FACE_TOP = 0.38   # куда по высоте кадра ставим центр лиц
HEAD = 0.9        # запас над лицом на макушку, в высотах лица

# Снимки, где каскад ошибается (принял за лицо светильник, блик, складку халата) и кадр
# приходится задать руками: at это где лицо на исходнике, put это куда его поставить
# в кадре, обе доли считаются от высоты сверху.
FRAMES = {
    "valiev-scholarship": {"at": 0.30, "put": 0.30},   # лицо Марии, сверху был потолок
    "melchakova-join": {"at": 0.39, "put": 0.50},      # портрет Юлии, срезало макушку
    # владелец сказал, что должно остаться в кадре (22.09.2026)
    "everest-2025": {"at": 0.50, "put": 0.50, "at_x": 0.49},          # Мартин почти в рост
    "photonics-expo-2025": {"at": 0.54, "put": 0.50, "at_x": 0.38},   # все трое у стенда
    "itmo-collab-2026": {"at": 0.50, "put": 0.50, "at_x": 0.53},      # Павел с микрофоном по центру
}
BLIND_TOP = 0.42  # то же, когда лиц не нашлось: кадр чуть выше середины


def faces_of(image):
    """Прямоугольники лиц на снимке. Пустой список, если лиц не нашлось.

    Каскад ловит и лишнее (узор на стене, блик на приборе), поэтому мелочь отсеиваем:
    остаются лица не меньше половины самого крупного и без наложений друг на друга.
    """
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)
    side = max(24, min(image.size) // 22)
    found = []
    for name in ("haarcascade_frontalface_default.xml", "haarcascade_profileface.xml"):
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + name)
        found += [tuple(int(v) for v in box) for box in
                  cascade.detectMultiScale(gray, 1.1, 6, minSize=(side, side))]
    if not found:
        return []
    found.sort(key=lambda b: b[2] * b[3], reverse=True)
    biggest = found[0]
    kept = []
    for x, y, w, h in found:
        if w < biggest[2] / 2:
            continue
        # то же лицо, найденное вторым каскадом, не считаем дважды
        if any(abs(x - kx) < kw / 2 and abs(y - ky) < kh / 2 for kx, ky, kw, kh in kept):
            continue
        # каскад принимает за лицо светильник на потолке или блик на приборе, и такой
        # ложный «сосед» уводит кадр. Люди на снимке стоят рядом, поэтому берем только тех,
        # кто держится возле самого крупного лица
        far = abs((y + h / 2) - (biggest[1] + biggest[3] / 2)) > 3 * biggest[3] \
            or abs((x + w / 2) - (biggest[0] + biggest[2] / 2)) > 4 * biggest[2]
        if far:
            continue
        kept.append((x, y, w, h))
    # одинокая мелкая находка это почти всегда не лицо: портрет снимают крупно,
    # а на групповом снимке лиц много. Тогда лучше кадрировать по центру
    if len(kept) < 3 and biggest[2] < min(image.size) * 0.05:
        return []
    return kept


def crop_box(size, faces, ratio, frame=None):
    """Самый большой кадр нужного соотношения, в который попадают все лица."""
    width, height = size
    if width / height <= ratio:
        crop_w, crop_h = width, width / ratio
    else:
        crop_w, crop_h = height * ratio, height

    if frame:
        # at и at_x это точка интереса на исходнике, put и put_x куда ее поставить в кадре
        x = width * frame.get("at_x", 0.5) - crop_w * frame.get("put_x", 0.5)
        y = height * frame["at"] - crop_h * frame["put"]
    elif len(faces):
        left = min(x for x, y, w, h in faces)
        right = max(x + w for x, y, w, h in faces)
        # каскад отмечает лицо без волос, поэтому сверху оставляем запас на макушку
        top = min(y - h * HEAD for x, y, w, h in faces)
        bottom = max(y + h for x, y, w, h in faces)
        x = (left + right) / 2 - crop_w / 2
        y = (top + bottom) / 2 - crop_h * FACE_TOP
        # лица не должны выпасть из кадра, когда группа стоит широко
        if bottom > y + crop_h:
            y = bottom - crop_h
        if top < y:
            y = top
        if right > x + crop_w:
            x = right - crop_w
        if left < x:
            x = left
    else:
        x = (width - crop_w) / 2
        y = (height - crop_h) * BLIND_TOP

    x = min(max(0, x), width - crop_w)
    y = min(max(0, y), height - crop_h)
    return (round(x), round(y), round(x + crop_w), round(y + crop_h))


def save(image, faces, name, width, ratio, dry, frame=None):
    # ratio None означает «снимок целиком», без кадрирования: так он идет в окно новости
    cut = image if ratio is None else image.crop(crop_box(image.size, faces, ratio, frame))
    if cut.width > width:
        cut = cut.resize((width, round(cut.height * width / cut.width)), Image.LANCZOS)
    if not dry:
        cut.save(IMG / name, "WEBP", quality=QUALITY, method=6)
    return f"{name} {cut.width}x{cut.height}"


def stamp(name):
    """Имя файла с меткой версии: новое фото ложится под тем же именем, и без метки
    браузеры показывали бы старый снимок из кэша."""
    path = IMG / name
    if not path.exists():
        return name
    return name + "?v=" + hashlib.sha1(path.read_bytes()).hexdigest()[:8]


def one_photo(items, path, news_id, dry):
    """Один снимок для одной новости: имя файла тогда не важно."""
    news = next((n for n in items if n["id"] == news_id), None)
    if not news:
        print("нет такой новости:", news_id)
        return False
    if not path.exists():
        print("нет файла:", path)
        return False
    image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    faces = faces_of(image)
    frame = FRAMES.get(news["id"])
    made = [save(image, faces, f"news-{news['id']}{suffix}.webp", width, ratio, dry, frame)
            for suffix, (width, ratio) in SIZES.items()]
    news["image"] = stamp(f"news-{news['id']}.webp")
    news["popupImage"] = stamp(f"news-{news['id']}-popup.webp")
    print(f"{path.name} -> {news_id}: исходник {image.width}x{image.height}, лиц {len(faces)}, "
          + ", ".join(made))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--src", default=str(SRC))
    ap.add_argument("--file", help="один снимок вместо папки")
    ap.add_argument("--for", dest="news_id", help="ид новости для этого снимка")
    args = ap.parse_args()

    items = json.loads(STORE.read_text(encoding="utf-8"))
    if args.file or args.news_id:
        if not (args.file and args.news_id):
            print("нужны оба ключа: --file и --for")
            return
        if one_photo(items, pathlib.Path(args.file), args.news_id, args.dry) and not args.dry:
            write_store(items)
            write_js(items)
            print("дальше: python tools/bump_assets.py и python tools/smoke.py")
        return

    by_form = {n["form"]: n for n in items if n.get("form")}
    src = pathlib.Path(args.src)
    if not src.exists():
        print("нет папки со снимками:", src)
        return

    done, skipped, blind, left = [], [], [], []
    for path in sorted(src.iterdir()):
        if path.name.lower() == "readme.md":  # пояснение к папке, а не снимок
            continue
        number = re.fullmatch(r"(\d+)", path.stem)
        if not number or path.suffix.lower() not in (".jpg", ".jpeg", ".png", ".jfif", ".webp"):
            skipped.append(path.name)
            continue
        news = by_form.get(int(number.group(1)))
        if not news:
            skipped.append(path.name + " (нет такой новости)")
            continue
        image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        faces = faces_of(image)
        if not len(faces):
            blind.append(path.name)
        frame = FRAMES.get(news["id"])
        made = [save(image, faces, f"news-{news['id']}{suffix}.webp", width, ratio, args.dry, frame)
                for suffix, (width, ratio) in SIZES.items()]
        news["image"] = stamp(f"news-{news['id']}.webp")
        news["popupImage"] = stamp(f"news-{news['id']}-popup.webp")
        done.append(f"{path.name}: лиц {len(faces)}, " + ", ".join(made))

    for news in items:
        if not news.get("image"):
            left.append(f"{news['id']} (новость {news.get('form', '?')} в анкете)")

    print(f"перенесено снимков: {len(done)}")
    for line in done:
        print("  " + line)
    if blind:
        print(f"лиц не нашлось, кадр по центру ({len(blind)}): " + ", ".join(blind))
    if skipped:
        print("пропущены файлы: " + ", ".join(skipped))
    if left:
        print(f"новости без фотографии ({len(left)}): " + ", ".join(left))
    if args.dry:
        print("сухой прогон, файлы не тронуты")
        return
    write_store(items)
    write_js(items)
    print("дальше: python tools/bump_assets.py и python tools/smoke.py")


if __name__ == "__main__":
    main()
