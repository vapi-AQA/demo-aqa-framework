"""Base Page Object with navigation, waiting and reporting helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from playwright.sync_api import Page

from aqa.config import Settings

from .expect import expect
from .steps import attach_screenshot, step


class BasePage:
    path = "/"

    def __init__(self, page: Page, settings: Settings):
        self.page = page
        self.settings = settings

    @step("open page | {self.path}")
    def open(self, path: str | None = None) -> None:
        target = path if path is not None else self.path
        if target.startswith("/"):
            target = urljoin(self.settings.base_url, target)
        self.page.goto(target, wait_until="domcontentloaded", timeout=self.settings.navigation_timeout_ms)
        self.page.wait_for_load_state("load")

    @step("wait for URL | {self.path}")
    def wait_for_url(self, pattern: str | Any, timeout: int | None = None) -> None:
        self.page.wait_for_url(pattern, timeout=timeout or self.settings.default_timeout_ms)

    @step("current URL")
    def current_url(self) -> str:
        return self.page.url

    @step("page title")
    def title(self) -> str:
        return self.page.title()

    def should_be_open(self, pattern: str | Any | None = None) -> None:
        expect(self.page).to_have_url(pattern or self.path)

    def screenshot(self, name: str = "page") -> Path:
        target = self.settings.artifacts_dir / f"{name}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(target), full_page=True)
        attach_screenshot(self.page, name)
        return target

    def reload(self) -> None:
        self.page.reload(wait_until="domcontentloaded")
