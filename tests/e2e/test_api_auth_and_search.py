import pytest

from aqa.api.client import ApiClient

pytestmark = pytest.mark.api


def test_health_endpoint(api_context, local_api):
    client = ApiClient(api_context, base_url=local_api)
    response = client.get("/api/health")
    assert response.json() == {"status": "ok"}


def test_secure_endpoint_rejects_missing_token(api_context, local_api):
    client = ApiClient(api_context, base_url=local_api)
    response = client.get("/api/secure", expected_status=401)
    assert response.json()["error"] == "unauthorized"


def test_secure_endpoint_accepts_token(api_context, local_api):
    client = ApiClient(api_context, base_url=local_api)
    response = client.get("/api/secure", headers={"Authorization": "Bearer token123"})
    assert response.json()["access"] == "granted"


def test_search_echoes_query(api_context, local_api):
    client = ApiClient(api_context, base_url=local_api)
    response = client.get("/api/search", params={"q": "playwright"})
    assert response.json()["q"] == "playwright"
    assert response.json()["items"] == ["playwright"]


def test_echo_endpoint_returns_payload_and_header(api_context, local_api):
    client = ApiClient(api_context, base_url=local_api)
    response = client.post(
        "/api/echo",
        body={"hello": "world"},
        headers={"X-Test": "value"},
    )
    assert response.json()["echo"] == {"hello": "world"}
    assert response.json()["headers"]["x-test"] == "value"


def test_unknown_endpoint_returns_404(api_context, local_api):
    client = ApiClient(api_context, base_url=local_api)
    response = client.get("/api/unknown", expected_status=404)
    assert response.json()["error"] == "not found"
