"""Чтение и запись файлов данных. Все JSON пишутся одинаково: UTF-8, отступ в один пробел,
перевод строки LF, в конце пустая строка. Так диф в git показывает только настоящие правки."""
import json

from .paths import ROOT

NL = "\n"


def load(path, default=None):
    """JSON из файла. Если файла нет, отдает default, а без default падает с понятной ошибкой."""
    if not path.exists():
        if default is not None:
            return default
        raise SystemExit(f"нет файла {rel(path)}")
    return json.loads(path.read_text(encoding="utf-8"))


def dumps(obj, sort_keys=False):
    return json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=sort_keys) + NL


def save(path, obj, sort_keys=False):
    write(path, dumps(obj, sort_keys))


def write(path, text):
    """Файлы бывают открыты у владельца в редакторе, тогда Windows не дает их переписать.
    Говорим об этом прямо, а не падаем со стеком вызовов."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(text, encoding="utf-8", newline=NL)
    except PermissionError:
        raise SystemExit(f"не смог записать {rel(path)}: файл открыт в другой программе, закройте его и запустите снова")


def rel(path):
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)
