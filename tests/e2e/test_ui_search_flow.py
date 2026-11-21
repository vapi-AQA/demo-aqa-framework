import re

import allure
import pytest

from aqa.core.expect import expect

pytestmark = [pytest.mark.live, pytest.mark.ui]


@allure.feature("Search")
def test_search_returns_results(main_page):
    main_page.open()
    main_page.open_search()
    main_page.search_dialog.search("locator")
    expect(main_page.search_dialog.input).to_have_value("locator")
    expect(main_page.search_dialog.first_hit_title).to_be_visible()


def test_search_escape_closes_and_keeps_url(main_page):
    main_page.open()
    initial_url = main_page.current_url()
    main_page.open_search()
    expect(main_page.search_dialog.root).to_be_visible()
    main_page.search_dialog.close()
    expect(main_page.search_dialog.root).to_be_hidden()
    assert main_page.current_url() == initial_url


def test_search_first_result_navigates(main_page):
    main_page.open()
    main_page.open_search()
    main_page.search_dialog.search("locator")
    expect(main_page.search_dialog.first_hit_title).to_be_visible()
    main_page.search_dialog.click_first_result()
    main_page.wait_for_url(re.compile(r"/docs/"))
