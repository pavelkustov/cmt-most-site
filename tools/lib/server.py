"""Локальный сервер для собранного сайта: смоук, замеры заголовков, просмотр.

Сайт раздается по тому же пути, что и в интернете (для GitHub Pages это /cmt-most-site/),
а на несуществующий адрес отвечает страницей 404.html, как GitHub Pages и nginx.
Так локально работает все, что зависит от адреса: страница «не найдено» и ее тег base.
"""
import contextlib
import http.server
import pathlib
import socketserver
import threading
import urllib.parse
from functools import partial

from .paths import DIST, SITE_INFO
from .store import load


def site_path():
    """Путь сайта из его адреса: https://pavelkustov.github.io/cmt-most-site/ -> /cmt-most-site/"""
    return urllib.parse.urlsplit(load(SITE_INFO)["url"]).path or "/"


class Handler(http.server.SimpleHTTPRequestHandler):
    prefix = "/"

    def log_message(self, *args):
        pass

    def handle_one_request(self):
        # браузер бросает лишние соединения (предзагрузка шрифтов), на Windows это ошибка в консоли
        try:
            super().handle_one_request()
        except (ConnectionAbortedError, ConnectionResetError):
            self.close_connection = True

    def translate_path(self, path):
        clean = urllib.parse.urlsplit(path).path
        if not clean.startswith(self.prefix):
            return "\0"   # вне сайта: такого файла нет, ответим 404
        return super().translate_path("/" + clean[len(self.prefix):])

    def send_error(self, code, message=None, explain=None):
        page = pathlib.Path(self.directory) / "404.html"
        if code != 404 or not page.exists():
            return super().send_error(code, message, explain)
        body = page.read_bytes()
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)


class Server(socketserver.ThreadingTCPServer):
    # многопоточный: браузер открывает несколько соединений сразу, на одном потоке страница зависает
    daemon_threads = True
    allow_reuse_address = True

    def handle_error(self, *args):
        pass


def make(root=DIST, port=0, prefix=None):
    prefix = prefix or site_path()
    handler = type("SiteHandler", (Handler,), {"prefix": prefix})
    httpd = Server(("127.0.0.1", port), partial(handler, directory=str(root)))
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}{prefix}"


@contextlib.contextmanager
def serve(root=DIST, prefix=None):
    """with serve() as base: base это адрес главной, например http://127.0.0.1:53211/cmt-most-site/"""
    httpd, base = make(root, 0, prefix)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        yield base
    finally:
        httpd.shutdown()
