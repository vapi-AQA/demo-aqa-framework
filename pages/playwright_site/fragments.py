"""Fragments for playwright.dev - only stable, scoped selectors."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from aqa.core.component import Component
from aqa.core.expect import expect
from aqa.core.steps import step


class HeaderFragment:
    def __init__(self, page: Page):
        self.page = page
        self.root: Locator = page.locator('nav[aria-label="Main"]')
        self.logo = Component(page, ".navbar__title", "Логотип", parent=self.root)
        self.docs_link = Component(page, 'a.navbar__link[href="/docs/intro"]', "Docs", parent=self.root)
        self.api_link = Component(page, 'a.navbar__link[href="/docs/api/class-playwright"]', "API", parent=self.root)
        self.mcp_link = Component(page, 'a.navbar__link[href="/mcp/introduction"]', "MCP", parent=self.root)
        self.language_trigger = Component(page, ".dropdown--hoverable > a", "Язык", parent=self.root)
        self.theme_toggle = Component(
            page, 'button[aria-label*="Switch between dark and light mode"]', "Тема", parent=self.root
        )
        self.search_button = Component(page, "button.DocSearch-Button", "Поиск", parent=self.root)
        self.github_link = Component(page, 'a[aria-label="GitHub repository"]', "GitHub", parent=self.root)

    def language_option(self, prefix: str) -> Component:
        return Component(self.page, f'a.dropdown__link[href="{prefix}"]', f"Язык {prefix}", parent=self.root)

    def should_be_complete(self) -> None:
        for item in (self.logo, self.docs_link, self.api_link, self.mcp_link, self.search_button, self.github_link):
            item.should_be_visible()

    def github_href(self) -> str | None:
        return self.github_link.get_attribute("href")


class SearchDialogFragment:
    def __init__(self, page: Page):
        self.page = page
        self.root: Locator = page.locator(".DocSearch-Modal:visible")
        self.input = Component(page, ".DocSearch-Input", "Поисковый запрос", parent=self.root)
        self.results = self.root.locator(".DocSearch-Dropdown")
        self.first_hit_title = Component(page, ".DocSearch-Hit-title >> nth=0", "Первый результат", parent=self.root)
        self.first_result = Component(page, ".DocSearch-Hit a >> nth=0", "Первый результат")

    @step("search | {query}")
    def search(self, query: str) -> None:
        self.input.fill(query)
        expect(self.results).to_be_visible()

    @step("click first result")
    def click_first_result(self) -> None:
        self.first_result.click()

    def close(self) -> None:
        self.page.keyboard.press("Escape")
