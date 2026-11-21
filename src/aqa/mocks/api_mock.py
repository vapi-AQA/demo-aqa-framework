"""Network mocking layer built on page.route with Allure logging."""

from __future__ import annotations

import json
import time
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any

from playwright.sync_api import Page, Route

from aqa.api.client import ApiClient
from aqa.core.steps import attach_json, step

_API_TYPES = ("xhr", "fetch")


@dataclass
class MockSpec:
    url: str
    method: str | None = None
    status: int = 200
    body: Any = None
    headers: dict[str, str] = field(default_factory=dict)
    content_type: str | None = None
    once: bool = False
    delay_ms: int = 0


class ApiMock:
    def __init__(self, page: Page):
        self.page = page
        self.specs: list[tuple[MockSpec, Any]] = []

    @staticmethod
    def _spec(spec_or_url: MockSpec | str, body: Any, options: dict) -> MockSpec:
        if isinstance(spec_or_url, MockSpec):
            return spec_or_url
        return MockSpec(url=spec_or_url, body=body, **options)

    @step("register API mock | {self._describe}")
    def mock(self, spec_or_url: MockSpec | str, body: Any = None, **options: Any) -> None:
        spec = self._spec(spec_or_url, body, options)
        spec.method = spec.method.upper() if spec.method else None
        consumed = {"value": False}

        def handler(route: Route) -> None:
            request = route.request
            if request.resource_type not in _API_TYPES or (spec.method and request.method != spec.method):
                route.fallback()
                return
            if spec.once and consumed["value"]:
                route.fallback()
                return
            consumed["value"] = True
            masked_headers = {
                key: ("***" if key.lower() in ApiClient.SENSITIVE_HEADERS else value)
                for key, value in request.headers.items()
            }
            attach_json(
                {"url": request.url, "method": request.method, "headers": masked_headers},
                name="mock: request",
            )
            if spec.delay_ms:
                time.sleep(spec.delay_ms / 1000)
            kwargs: dict[str, Any] = {"status": spec.status, "headers": spec.headers or None}
            if spec.body is None:
                if spec.content_type:
                    kwargs["content_type"] = spec.content_type
            elif not spec.content_type or "json" in spec.content_type:
                kwargs["json"] = spec.body
            else:
                kwargs["body"] = spec.body if isinstance(spec.body, str) else json.dumps(spec.body)
                kwargs["content_type"] = spec.content_type
            route.fulfill(**kwargs)
            if spec.once:
                self._unregister(spec, handler)

        self.page.route(spec.url, handler)
        self.specs.append((spec, handler))

    @property
    def _describe(self) -> str:
        return ", ".join(f"{spec.method or 'ANY'} {spec.url}" for spec, _ in self.specs[-1:])

    def get(self, url: str, body: Any = None, **options: Any) -> None:
        self.mock(url, body, method="GET", **options)

    def post(self, url: str, body: Any = None, **options: Any) -> None:
        self.mock(url, body, method="POST", **options)

    def _unregister(self, spec: MockSpec, handler: Any) -> None:
        # unroute can fail if the page/context is already closed; reset must still finish.
        with suppress(Exception):
            self.page.unroute(spec.url, handler)
        self.specs = [(s, h) for s, h in self.specs if not (s is spec and h is handler)]

    @step("reset API mocks")
    def reset(self) -> None:
        for spec, handler in list(self.specs):
            self._unregister(spec, handler)
        self.specs.clear()
