"""Проверки с Allure-шагами + паттерн soft assertions.

Hard assertions: `expect(locator).to_be_visible()`.
Soft assertions: `with soft_assert() as verify: ... verify.to_be_visible(...)` -
все падения собираются и выбрасываются одним сообщением в конце блока.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import allure
from playwright.sync_api import Locator
from playwright.sync_api import expect as pw_expect


def _resolve(subject: Any) -> Any:
    for attr in ("element", "locator", "root"):
        value = getattr(subject, attr, None)
        if isinstance(value, Locator):
            return value
    return subject


class AllureExpect:
    def __init__(self, subject: Any, description: str | None = None):
        self.subject = _resolve(subject)
        self.description = description or getattr(subject, "name", None) or "element"

    def _run(self, title: str, action: Callable[[], None]) -> None:
        with allure.step(f"{title} | {self.description}"):
            action()

    # --- locator matchers --------------------------------------------------
    def to_be_visible(self) -> None:
        self._run("visible", lambda: pw_expect(self.subject).to_be_visible())

    def to_be_hidden(self) -> None:
        self._run("hidden", lambda: pw_expect(self.subject).to_be_hidden())

    def to_be_enabled(self) -> None:
        self._run("enabled", lambda: pw_expect(self.subject).to_be_enabled())

    def to_be_disabled(self) -> None:
        self._run("disabled", lambda: pw_expect(self.subject).to_be_disabled())

    def to_be_editable(self) -> None:
        self._run("editable", lambda: pw_expect(self.subject).to_be_editable())

    def to_have_text(self, expected: Any) -> None:
        self._run(f"text={expected!r}", lambda: pw_expect(self.subject).to_have_text(expected))

    def to_have_value(self, expected: Any) -> None:
        self._run(f"value={expected!r}", lambda: pw_expect(self.subject).to_have_value(expected))

    def to_have_attribute(self, name: str, expected: Any) -> None:
        self._run(f"attr {name}={expected!r}", lambda: pw_expect(self.subject).to_have_attribute(name, expected))

    def to_have_class(self, expected: Any) -> None:
        self._run(f"class={expected!r}", lambda: pw_expect(self.subject).to_have_class(expected))

    def to_have_count(self, expected: int) -> None:
        self._run(f"count={expected}", lambda: pw_expect(self.subject).to_have_count(expected))

    def to_have_url(self, expected: Any) -> None:
        self._run(f"url={expected!r}", lambda: pw_expect(self.subject).to_have_url(expected))

    # --- value matchers ----------------------------------------------------
    def to_be_number(self) -> None:
        self._type_check("number", lambda s: isinstance(s, (int, float)) and not isinstance(s, bool))

    def to_be_string(self) -> None:
        self._type_check("string", lambda s: isinstance(s, str))

    def to_be_boolean(self) -> None:
        self._type_check("boolean", lambda s: isinstance(s, bool))

    def to_be_array(self) -> None:
        self._type_check("array", lambda s: isinstance(s, (list, tuple)))

    def to_be_object(self) -> None:
        self._type_check("object", lambda s: isinstance(s, dict))

    def _type_check(self, expected: str, predicate) -> None:
        def action() -> None:
            assert predicate(self.subject), f"expected {expected}, got {type(self.subject).__name__}"

        self._run(f"type={expected}", action)


class SoftAssertions:
    """Collect failures instead of stopping at the first one."""

    def __init__(self) -> None:
        self.failures: list[str] = []

    def __enter__(self) -> SoftAssertions:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if self.failures:
            raise AssertionError("\n".join(f"{i}) {msg}" for i, msg in enumerate(self.failures, 1)))
        return False

    def expect(self, subject: Any, description: str | None = None) -> AllureExpect:
        return AllureExpect(subject, description)

    def _soft(self, subject: Any, description: str | None, matcher: str, *args: Any) -> None:
        try:
            getattr(self.expect(subject, description), matcher)(*args)
        except AssertionError as error:
            self.failures.append(f"{description or getattr(subject, 'name', 'element')}: {error}")

    def to_be_visible(self, subject: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_be_visible")

    def to_be_hidden(self, subject: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_be_hidden")

    def to_be_enabled(self, subject: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_be_enabled")

    def to_have_text(self, subject: Any, expected: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_have_text", expected)

    def to_have_value(self, subject: Any, expected: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_have_value", expected)

    def to_have_attribute(self, subject: Any, name: str, expected: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_have_attribute", name, expected)

    def to_be_checked(self, subject: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_be_checked")

    def to_be_disabled(self, subject: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_be_disabled")

    def to_be_editable(self, subject: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_be_editable")

    def to_be_focused(self, subject: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_be_focused")

    def to_contain_text(self, subject: Any, expected: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_contain_text", expected)

    def to_have_class(self, subject: Any, expected: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_have_class", expected)

    def to_have_count(self, subject: Any, expected: int, description: str | None = None) -> None:
        self._soft(subject, description, "to_have_count", expected)

    def to_have_css(self, subject: Any, expected: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_have_css", expected)

    def to_have_id(self, subject: Any, expected: Any, description: str | None = None) -> None:
        self._soft(subject, description, "to_have_id", expected)

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)


def expect(subject: Any, description: str | None = None) -> AllureExpect:
    return AllureExpect(subject, description)


def soft_assert() -> SoftAssertions:
    return SoftAssertions()
