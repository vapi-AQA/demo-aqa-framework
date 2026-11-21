"""API client: one method = one Allure step, retries, schema contracts."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode, urljoin

from playwright.sync_api import APIRequestContext, APIResponse

from aqa.core.steps import attach_json, step

from .schema import validate_schema


@dataclass(frozen=True, slots=True)
class ApiResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    data: Any

    def json(self) -> Any:
        return self.data


class ApiClient:
    RETRIABLE_STATUSES = {408, 429, 500, 502, 503, 504}
    IDEMPOTENT_METHODS = {"GET", "PUT", "DELETE", "HEAD", "OPTIONS"}
    SENSITIVE_HEADERS = {"authorization", "cookie", "x-api-key"}

    def __init__(self, context: APIRequestContext, base_url: str = "", default_headers: dict | None = None):
        self.context = context
        self.base_url = base_url.rstrip("/") + "/" if base_url else ""
        self.default_headers = default_headers or {}

    def _url(self, path: str, params: dict | None) -> str:
        url = path if path.startswith("http") else urljoin(self.base_url, path.lstrip("/"))
        if params:
            url += ("&" if "?" in url else "?") + urlencode(params, doseq=True)
        return url

    @step(lambda _self, method, path, *_args, **_kwargs: f"{method.upper()} {path}")
    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        body: Any = None,
        headers: dict | None = None,
        schema: dict | None = None,
        expected_status: int | None = None,
        retries: int = 0,
    ) -> ApiResponse:
        url = self._url(path, params)
        retries = max(0, retries)
        merged_headers = {**self.default_headers, **(headers or {})}
        if body is not None and "Content-Type" not in merged_headers:
            merged_headers["Content-Type"] = "application/json"

        def send() -> tuple[APIResponse, bytes]:
            response = self.context.fetch(
                url,
                method=method.upper(),
                headers=merged_headers,
                data=json.dumps(body, ensure_ascii=False) if body is not None else None,
                timeout=30_000,
            )
            return response, response.body()

        last_status = 0
        for attempt in range(retries + 1):
            response, raw = send()
            last_status = response.status
            if (
                method.upper() not in self.IDEMPOTENT_METHODS
                or last_status not in self.RETRIABLE_STATUSES
                or attempt == retries
            ):
                break
            time.sleep(0.3 * (2**attempt))

        try:
            parsed = json.loads(raw) if raw else None
        except ValueError:
            parsed = raw.decode("utf-8", errors="replace")

        safe_headers = {k: ("***" if k.lower() in self.SENSITIVE_HEADERS else v) for k, v in merged_headers.items()}
        attach_json(
            {"method": method.upper(), "url": url, "headers": safe_headers, "body": body},
            name="request",
        )
        attach_json({"status": last_status, "headers": response.headers, "body": parsed}, name="response")

        if expected_status is not None:
            assert last_status == expected_status, f"expected {expected_status}, got {last_status} for {method} {url}"
        if schema is not None:
            validate_schema(parsed, schema)
        return ApiResponse(status=last_status, headers=response.headers, body=raw, data=parsed)

    def get(self, path: str, **kwargs: Any) -> ApiResponse:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> ApiResponse:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> ApiResponse:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> ApiResponse:
        return self.request("DELETE", path, **kwargs)
