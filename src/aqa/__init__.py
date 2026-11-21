"""AQA framework - modern pytest + Playwright test automation template."""

from aqa.api.client import ApiClient, ApiResponse
from aqa.config import Credentials, Settings
from aqa.core.component import Component
from aqa.core.expect import SoftAssertions, expect, soft_assert
from aqa.core.page import BasePage
from aqa.core.steps import attach_json, attach_screenshot, step
from aqa.data.factories import DataFactory
from aqa.mocks.api_mock import ApiMock

__all__ = [
    "Settings",
    "Credentials",
    "Component",
    "BasePage",
    "expect",
    "soft_assert",
    "SoftAssertions",
    "step",
    "attach_json",
    "attach_screenshot",
    "ApiClient",
    "ApiResponse",
    "ApiMock",
    "DataFactory",
]
