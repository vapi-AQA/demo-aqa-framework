from __future__ import annotations

import re

from playwright.sync_api import Page

from aqa.config import Settings
from aqa.core.component import Component
from aqa.core.page import BasePage

from .fragments import HeaderFragment


class DocsPage(BasePage):
    path = "/docs/intro"

    def __init__(self, page: Page, settings: Settings):
        super().__init__(page, settings)
        self.header = HeaderFragment(page)
        self.heading = Component(page, "main h1, article h1, h1", "Заголовок документации")
        self.article = Component(page, "main article, article", "Контент документации")

    def should_be_opened(self) -> None:
        self.wait_for_url(re.compile(r"/docs/"))
        self.heading.should_be_visible()
