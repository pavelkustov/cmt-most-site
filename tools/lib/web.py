"""Запросы к открытым сервисам (Crossref, OpenAlex, Semantic Scholar, Europe PMC).

Ответы кэшируются на диске в %TEMP%: повторный прогон чужие сервисы не дергает, а у OpenAlex
дневной лимит. Неудачный ответ не кэшируется, в следующий раз его спросят снова.
"""
import hashlib
import json
import pathlib
import tempfile
import time
import urllib.request

MAILTO = "bridge@metalab.ifmo.ru"
UA = {"User-Agent": f"cmt-most-site/1.0 (mailto:{MAILTO})"}
TEMP = pathlib.Path(tempfile.gettempdir())


def get_json(url, cache=None, tries=1, pause=0.0, offline=False, wait_429=20, timeout=45):
    """Ответ сервиса как словарь, при любой ошибке пустой словарь.

    cache      имя папки кэша в %TEMP% (у каждого скрипта своя, как повелось)
    tries      сколько раз пробовать; повтор имеет смысл только при 429 (лимит запросов)
    pause      пауза после каждого сетевого запроса, чтобы не упираться в лимиты
    offline    только кэш, в сеть не ходить
    """
    box = TEMP / cache / (hashlib.sha1(url.encode()).hexdigest() + ".json") if cache else None
    if box and box.exists():
        return json.loads(box.read_text(encoding="utf-8"))
    if offline:
        return {}
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as f:
                data = json.load(f)
            if box:
                box.parent.mkdir(exist_ok=True)
                box.write_text(json.dumps(data), encoding="utf-8")
            return data
        except Exception as e:
            if "429" in str(e) and attempt < tries - 1:
                time.sleep(wait_429)
                continue
            return {}
        finally:
            if pause:
                time.sleep(pause)
    return {}


def crossref(doi, cache=None, **kw):
    """Запись Crossref о работе (поле message), пустой словарь, если записи нет."""
    return get_json("https://api.crossref.org/works/" + doi, cache=cache, **kw).get("message") or {}


def openalex(doi, cache=None, **kw):
    """Запись OpenAlex о работе строго по DOI: поиск по названию находит чужое."""
    return get_json("https://api.openalex.org/works/doi:" + doi, cache=cache, **kw)
