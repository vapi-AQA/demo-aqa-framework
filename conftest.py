"""Global fixtures and reporting hooks.

Правило: тесты НЕ создают зависимости сами - всё приходит через фикстуры.
"""

from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import allure
import pytest

from aqa.config import Settings
from aqa.core.steps import attach_screenshot
from aqa.mocks.api_mock import ApiMock

LIVE_TESTS_ENABLED = os.getenv("RUN_LIVE_TESTS") == "1"


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session")
def api_context(playwright, settings: Settings):
    context = playwright.request.new_context(ignore_https_errors=True)
    yield context
    context.dispose()


@pytest.fixture(scope="session")
def local_api():
    """In-process HTTP server: API-тесты не зависят от внешнего стенда."""
    flaky_attempts: dict[str, int] = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def _read_json(self) -> dict:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            return json.loads(raw or b"{}")

        def _send(self, status: int, payload: dict | None = None) -> None:
            body = b"" if payload is None else json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def _route(self, method: str, body: dict | None = None) -> None:
            from urllib.parse import parse_qs, urlparse

            parsed = urlparse(self.path)
            path = parsed.path
            qs = {key: values[0] for key, values in parse_qs(parsed.query).items()}

            if method == "GET" and path == "/api/health":
                self._send(200, {"status": "ok"})
                return
            if method == "GET" and path == "/api/users":
                items = [
                    {"id": 1, "email": "user1@example.com", "role": "admin"},
                    {"id": 2, "email": "user2@example.com", "role": "member"},
                ]
                page = int(qs.get("page", "1"))
                limit = int(qs.get("limit", "10"))
                self._send(200, {"items": items, "total": len(items), "page": page, "limit": limit})
                return
            if method == "GET" and path == "/api/users/1":
                self._send(200, {"id": 1, "email": "user@example.com", "role": "admin"})
                return
            if method == "GET" and path == "/api/users/999":
                self._send(404, {"error": "not found"})
                return
            if method == "GET" and path == "/api/search":
                self._send(200, {"q": qs.get("q", ""), "items": [qs.get("q", "")] if qs.get("q") else []})
                return
            if method == "GET" and path == "/api/secure":
                token = self.headers.get("Authorization", "")
                if token == "Bearer token123":
                    self._send(200, {"access": "granted"})
                else:
                    self._send(401, {"error": "unauthorized"})
                return
            if method == "GET" and path == "/api/flaky":
                token = self.headers.get("X-Flaky-Token", "default")
                flaky_attempts[token] = flaky_attempts.get(token, 0) + 1
                count = flaky_attempts[token]
                if count < 3:
                    self._send(503, {"error": "temporarily unavailable", "attempt": count})
                else:
                    self._send(200, {"ok": True, "attempt": count})
                return
            if method == "POST" and path == "/api/users":
                payload = body or {}
                self._send(201, {"id": 2, **payload})
                return
            if method == "POST" and path == "/api/echo":
                self._send(200, {"echo": body or {}, "headers": {"x-test": self.headers.get("X-Test", "")}})
                return
            if method == "PUT" and path == "/api/users/1":
                payload = body or {}
                self._send(200, {"id": 1, **payload})
                return
            if method == "DELETE" and path == "/api/users/1":
                self._send(204, None)
                return
            self._send(404, {"error": "not found"})

        def do_GET(self):
            self._route("GET")

        def do_POST(self):
            self._route("POST", self._read_json())

        def do_PUT(self):
            self._route("PUT", self._read_json())

        def do_DELETE(self):
            self._route("DELETE")

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.fixture
def api_mock(page) -> ApiMock:
    mock = ApiMock(page)
    yield mock
    mock.reset()


@pytest.fixture
def main_page(page, settings: Settings):
    from pages.playwright_site.main_page import MainPage

    return MainPage(page, settings)


@pytest.fixture
def docs_page(page, settings: Settings):
    from pages.playwright_site.docs_page import DocsPage

    return DocsPage(page, settings)


@pytest.fixture(scope="session")
def browser_context_args() -> dict:
    settings = Settings.from_env()
    return {
        "base_url": settings.base_url,
        "viewport": {"width": settings.viewport_width, "height": settings.viewport_height},
        "locale": settings.locale,
        "ignore_https_errors": True,
    }


def pytest_configure(config) -> None:
    try:
        results_dir = config.getoption("--alluredir")
    except ValueError:
        results_dir = None
    if results_dir:
        target = Path(results_dir)
        target.mkdir(parents=True, exist_ok=True)
        info = Settings.from_env().environment_info()
        (target / "environment.properties").write_text(
            "\n".join(f"{key}={value}" for key, value in info.items()), encoding="utf-8"
        )


def pytest_collection_modifyitems(items) -> None:
    if LIVE_TESTS_ENABLED:
        return
    skip = pytest.mark.skip(reason="внешний доступ выключен: RUN_LIVE_TESTS=1")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page is not None:
            attach_screenshot(page, name=f"failure-{item.name}")
            allure.dynamic.description_html(
                f"<p><b>Test:</b> {item.name}</p><p><b>Error:</b> {report.longreprtext[-1000:]}</p>"
            )
