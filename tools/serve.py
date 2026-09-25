"""Локальный просмотр: собирает сайт и открывает его на http://127.0.0.1:8000/cmt-most-site/

    python tools/serve.py            собрать и раздавать, пока окно открыто (Ctrl+C остановит)
    python tools/serve.py --port 8080

Сайт раздается по тому же пути, что и в интернете, и на несуществующий адрес отвечает
страницей 404, как хостинг. После правки исходников сайт надо собрать заново:
остановить и запустить снова.
"""
import argparse
import sys
import webbrowser

import build
from lib.paths import DIST
from lib.server import make


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-open", action="store_true", help="не открывать браузер")
    args = ap.parse_args()
    if not build.build():
        sys.exit(1)
    httpd, base = make(DIST, args.port)
    print("сайт:", base, " (Ctrl+C остановит)")
    if not args.no_open:
        webbrowser.open(base)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
