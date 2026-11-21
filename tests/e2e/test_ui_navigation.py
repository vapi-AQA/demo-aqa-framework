import re

import allure
import pytest

pytestmark = [pytest.mark.live, pytest.mark.ui]


@allure.feature("Navigation")
@pytest.mark.parametrize(
    "link_name,expected",
    [
        ("docs_link", re.compile(r"/docs/intro")),
        ("api_link", re.compile(r"/docs/api")),
        ("mcp_link", re.compile(r"/mcp/introduction")),
    ],
)
def test_header_navigation(main_page, link_name, expected):
    main_page.open()
    getattr(main_page.header, link_name).click()
    main_page.wait_for_url(expected)


def test_docs_page_contains_content(main_page, docs_page):
    main_page.open()
    main_page.open_docs()
    docs_page.should_be_opened()
