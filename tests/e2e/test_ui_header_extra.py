import re

import allure
import pytest

from aqa.core.expect import expect, soft_assert

pytestmark = [pytest.mark.live, pytest.mark.ui]


@allure.feature("Header")
def test_header_elements_and_attributes(main_page):
    main_page.open()
    header = main_page.header
    with soft_assert() as verify:
        verify.to_be_visible(header.root, "Header root")
        verify.to_be_visible(header.logo, "Logo")
        verify.to_be_visible(header.docs_link, "Docs link")
        verify.to_be_visible(header.api_link, "API link")
        verify.to_be_visible(header.mcp_link, "MCP link")
        verify.to_be_visible(header.search_button, "Search button")
        verify.to_be_visible(header.github_link, "GitHub link")
    expect(header.logo).to_have_text(re.compile("Playwright", re.IGNORECASE))


def test_github_link_points_to_repository(main_page):
    main_page.open()
    href = main_page.header.github_href() or ""
    assert "github.com" in href or "microsoft/playwright" in href


def test_theme_toggle_is_clickable(main_page):
    main_page.open()
    toggle = main_page.header.theme_toggle
    expect(toggle).to_be_visible()
    toggle.click()


def test_language_menu_opens_on_hover(main_page, page):
    main_page.open()
    main_page.header.language_trigger.hover()
    option = main_page.header.language_option("/python/")
    expect(option).to_be_visible()
    option.click()
    main_page.wait_for_url(re.compile(r"/python/"))
