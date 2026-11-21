from __future__ import annotations

import re

from playwright.sync_api import Page

from aqa.config import Settings
from aqa.core.expect import expect
from aqa.core.page import BasePage

from .fragments import HeaderFragment, SearchDialogFragment


class MainPage(BasePage):
    path = "/"

    def __init__(self, page: Page, settings: Settings):
        super().__init__(page, settings)
        self.header = HeaderFragment(page)
        self.search_dialog = SearchDialogFragment(page)

    def open_search(self) -> None:
        self.header.search_button.click()
        expect(self.search_dialog.root).to_be_visible()

    def open_docs(self) -> None:
        self.header.docs_link.click()
        self.wait_for_url(re.compile(r"/docs/intro"))
