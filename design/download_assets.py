"""Скачивает ассеты из Figma по assets_manifest.txt (ссылки живут ~7 дней)."""
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "design" / "assets_manifest.txt"

ok, failed = 0, []
for line in MANIFEST.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    name, url = line.split(None, 1)
    target = ROOT / name if name.startswith("design/") else ROOT / "assets" / name
    if target.exists() and target.stat().st_size > 0:
        ok += 1
        continue
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        # без User-Agent Figma отвечает 202 с пустым телом
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        if r.status != 200 or not data:
            raise RuntimeError(f"HTTP {r.status}, {len(data)} bytes")
        target.write_bytes(data)
        ok += 1
    except Exception as e:
        failed.append(f"{name}: {e}")

print(f"ok {ok}, failed {len(failed)}")
for f in failed:
    print("  ", f)
