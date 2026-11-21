import pytest

from aqa.mocks.api_mock import MockSpec

pytestmark = [pytest.mark.api, pytest.mark.live]


def test_mock_with_spec(page, api_mock):
    api_mock.mock(
        MockSpec(
            url="**/api/mock-demo",
            method="GET",
            status=201,
            body={"source": "mock"},
            content_type="application/json",
        )
    )
    page.goto("https://playwright.dev/")
    result = page.evaluate("fetch('/api/mock-demo').then(async r => ({status: r.status, body: await r.json()}))")
    assert result == {"status": 201, "body": {"source": "mock"}}


def test_once_mock_falls_back(page, api_mock):
    api_mock.get("**/api/once", {"hit": True}, once=True)
    page.goto("https://playwright.dev/")
    first = page.evaluate("fetch('/api/once').then(r => r.json())")
    assert first == {"hit": True}
    api_mock.reset()
