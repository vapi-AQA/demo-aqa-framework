.PHONY: install lint format test test-live report clean

install:
	pip install -e ".[dev]"
	playwright install chromium

lint:
	ruff check .

format:
	ruff format .

test:
	pytest tests/unit tests/e2e/test_api_contract.py tests/e2e/test_api_mock.py tests/e2e/test_api_users.py tests/e2e/test_api_validation.py tests/e2e/test_api_auth_and_search.py

test-live:
	RUN_LIVE_TESTS=1 pytest -n auto --alluredir=allure-results

report:
	allure generate allure-results --clean -o allure-report
	allure open allure-report

clean:
	rm -rf allure-results allure-report artifacts .pytest_cache
