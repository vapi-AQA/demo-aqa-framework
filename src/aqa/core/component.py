"""Page Object building block: atomic UI component."""

from __future__ import annotations

from typing import Any

from playwright.sync_api import Locator, Page

from .expect import expect
from .steps import step


class Component:
    def __init__(self, page: Page, selector: str | Locator, name: str = "element", parent: Locator | None = None):
        self.page = page
        self.name = name
        if isinstance(selector, Locator):
            self.element = selector
        elif parent is not None:
            self.element = parent.locator(selector)
        else:
            self.element = page.locator(selector)

    # --- actions -----------------------------------------------------------
    @step("click | {self.name}")
    def click(self, **kwargs: Any) -> None:
        self.element.click(**kwargs)

    @step("hover | {self.name}")
    def hover(self) -> None:
        self.element.hover()

    @step("fill | {self.name}")
    def fill(self, value: str, **kwargs: Any) -> None:
        self.element.fill(value, **kwargs)

    @step("clear | {self.name}")
    def clear(self) -> None:
        self.element.fill("")

    @step("check | {self.name}")
    def check(self, **kwargs: Any) -> None:
        self.element.check(**kwargs)

    @step("uncheck | {self.name}")
    def uncheck(self, **kwargs: Any) -> None:
        self.element.uncheck(**kwargs)

    @step("select_option | {self.name}")
    def select_option(self, value: Any, **kwargs: Any) -> list[str]:
        return self.element.select_option(value, **kwargs)

    # --- queries -----------------------------------------------------------
    @step("text | {self.name}")
    def text(self) -> str:
        return (self.element.text_content() or "").strip()

    @step("input_value | {self.name}")
    def input_value(self) -> str:
        return self.element.input_value()

    @step("get_attribute | {self.name}")
    def get_attribute(self, name: str) -> str | None:
        return self.element.get_attribute(name)

    def count(self) -> int:
        return self.element.count()

    def is_visible(self) -> bool:
        return self.element.is_visible()

    # --- assertions --------------------------------------------------------
    def should_be_visible(self) -> None:
        expect(self).to_be_visible()

    def should_be_hidden(self) -> None:
        expect(self).to_be_hidden()

    def should_have_text(self, expected: Any) -> None:
        expect(self).to_have_text(expected)

    def should_have_value(self, expected: Any) -> None:
        expect(self).to_have_value(expected)

    def should_have_attribute(self, name: str, expected: Any) -> None:
        expect(self).to_have_attribute(name, expected)
