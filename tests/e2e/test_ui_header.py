import re

import allure
import pytest

from aqa.core.expect import soft_assert

pytestmark = [pytest.mark.live, pytest.mark.ui, pytest.mark.smoke]


@allure.epic("Playwright site")
@allure.feature("Header")
def test_header_and_navigation(main_page):
    main_page.open()
    with soft_assert() as verify:
        verify.to_be_visible(main_page.header.root, "Header root")
        verify.to_be_visible(main_page.header.logo, "Logo")
        verify.to_be_visible(main_page.header.search_button, "Search button")
        verify.to_have_text(main_page.header.logo, re.compile("Playwright"))

    main_page.open_docs()
    main_page.should_be_open(re.compile(r"/docs/intro"))
