import aqa.api.client as client_module
from aqa.api.client import ApiClient


class _Response:
    def __init__(self, status: int):
        self.status = status
        self.headers = {}

    def body(self) -> bytes:
        return b'{"ok": true}'


class _Context:
    def __init__(self, statuses):
        self._statuses = list(statuses)
        self.calls = 0

    def fetch(self, url, **kwargs):
        self.calls += 1
        status = self._statuses.pop(0) if self._statuses else 200
        return _Response(status)


def test_retries_only_idempotent_methods(monkeypatch):
    monkeypatch.setattr(client_module.time, "sleep", lambda *_: None)

    get_ctx = _Context([503, 503, 200])
    ApiClient(get_ctx).get("/flaky", retries=2)
    assert get_ctx.calls == 3

    post_ctx = _Context([503, 503, 200])
    ApiClient(post_ctx).post("/flaky", retries=2)
    assert post_ctx.calls == 1


def test_request_attachment_redacts_secrets(monkeypatch):
    attachments = []
    monkeypatch.setattr(client_module, "attach_json", lambda payload, name: attachments.append((name, payload)))

    client = ApiClient(_Context([200]), default_headers={"Authorization": "Bearer secret", "X-Api-Key": "key123"})
    client.get("/secure", headers={"Cookie": "session=abc"})

    request_payload = next(payload for name, payload in attachments if name == "request")
    assert request_payload["headers"]["Authorization"] == "***"
    assert request_payload["headers"]["X-Api-Key"] == "***"
    assert request_payload["headers"]["Cookie"] == "***"
