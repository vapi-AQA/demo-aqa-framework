"""Единообразные Allure-шаги и вложения."""

from __future__ import annotations

import functools
import inspect
import json
from collections.abc import Callable
from contextlib import suppress
from typing import Any

import allure
from playwright.sync_api import Page


def step(description: str | Callable[..., str]):
    """Decorator for POM/API methods: one method == one named Allure step."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if callable(description):
                title = description(*args, **kwargs)
            elif "{" in description:
                try:
                    bound = inspect.signature(func).bind(*args, **kwargs)
                    bound.apply_defaults()
                    title = description.format(*args, **bound.arguments)
                except Exception:
                    try:
                        title = description.format(*args, **kwargs)
                    except Exception:
                        title = description
            else:
                title = description
            with allure.step(title or func.__name__):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def attach_json(data: Any, name: str = "data") -> None:
    allure.attach(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def attach_screenshot(page: Page, name: str = "screenshot") -> None:
    # The page may be closed already; a missing screenshot must not hide the test failure.
    with suppress(Exception):
        allure.attach(page.screenshot(full_page=True), name=name, attachment_type=allure.attachment_type.PNG)
