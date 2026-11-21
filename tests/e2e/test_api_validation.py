import pytest

from aqa.api.client import ApiClient

pytestmark = pytest.mark.api

INVALID_USER_SCHEMA = {
    "type": "object",
    "properties": {"id": {"type": "integer"}, "email": {"type": "string"}, "extra": {"type": "string"}},
    "required": ["id", "email", "extra"],
}


def test_status_mismatch_raises(api_context, local_api):
    client = ApiClient(api_context, base_url=local_api)
    with pytest.raises(AssertionError, match="expected 201, got 200"):
        client.get("/api/health", expected_status=201)


def test_schema_validation_raises_on_contract_violation(api_context, local_api):
    client = ApiClient(api_context, base_url=local_api)
    with pytest.raises(AssertionError, match="Schema validation failed"):
        client.get("/api/users/1", schema=INVALID_USER_SCHEMA)


def test_expected_status_can_be_disabled(api_context, local_api):
    client = ApiClient(api_context, base_url=local_api)
    response = client.get("/api/users/999", expected_status=None)
    assert response.status == 404
