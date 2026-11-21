import uuid

import allure
import pytest

from aqa.api.client import ApiClient
from tests.e2e.test_api_users import USER_SCHEMA

pytestmark = pytest.mark.api


@allure.epic("API")
@allure.feature("Contract")
def test_get_user_contract(api_context, local_api):
    client = ApiClient(api_context, base_url=local_api)
    response = client.get("/api/users/1", schema=USER_SCHEMA, expected_status=200)
    assert response.json()["id"] == 1


def test_post_echo(api_context, local_api):
    client = ApiClient(api_context, base_url=local_api)
    response = client.post("/api/users", body={"name": "AQA"}, expected_status=201)
    assert response.status == 201
    assert response.json()["name"] == "AQA"


def test_retry_on_retriable_status(api_context, local_api):
    client = ApiClient(api_context, base_url=local_api)
    token = uuid.uuid4().hex
    response = client.get("/api/flaky", headers={"X-Flaky-Token": token}, retries=3, expected_status=200)
    assert response.json()["ok"] is True
    assert response.json()["attempt"] == 3
