import pytest

from aqa.api.client import ApiClient

pytestmark = pytest.mark.api


@pytest.fixture
def api_client(api_context, local_api):
    return ApiClient(api_context, base_url=local_api)


LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {"type": "array"},
        "total": {"type": "integer"},
        "page": {"type": "integer"},
        "limit": {"type": "integer"},
    },
    "required": ["items", "total"],
}

USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "email": {"type": "string"},
        "role": {"type": "string"},
    },
    "required": ["id", "email"],
}


def test_list_users(api_context, local_api, api_client):
    client = api_client
    response = client.get("/api/users", schema=LIST_SCHEMA)
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 2


def test_list_users_with_pagination_params(api_context, local_api, api_client):
    client = api_client
    response = client.get("/api/users", params={"page": 2, "limit": 5})
    assert response.json()["page"] == 2
    assert response.json()["limit"] == 5


def test_get_user_by_id(api_context, local_api, api_client):
    client = api_client
    response = client.get("/api/users/1", schema=USER_SCHEMA)
    assert response.json()["id"] == 1
    assert response.json()["email"] == "user@example.com"


def test_get_missing_user_returns_404(api_context, local_api, api_client):
    client = api_client
    response = client.get("/api/users/999", expected_status=404)
    assert response.json()["error"] == "not found"


def test_create_user(api_context, local_api, api_client):
    client = api_client
    response = client.post("/api/users", body={"name": "AQA", "email": "aqa@example.com"}, expected_status=201)
    assert response.status == 201
    assert response.json()["name"] == "AQA"
    assert response.json()["id"] == 2


def test_update_user(api_context, local_api, api_client):
    client = api_client
    response = client.put("/api/users/1", body={"email": "new@example.com"})
    assert response.status == 200
    assert response.json()["email"] == "new@example.com"


def test_delete_user(api_context, local_api, api_client):
    client = api_client
    response = client.delete("/api/users/1", expected_status=204)
    assert response.status == 204
