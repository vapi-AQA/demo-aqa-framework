from aqa.mocks.api_mock import MockSpec


def test_mock_spec_defaults():
    spec = MockSpec(url="**/api/test")
    assert spec.url == "**/api/test"
    assert spec.method is None
    assert spec.status == 200
    assert spec.body is None
    assert spec.headers == {}
    assert spec.content_type is None
    assert spec.once is False
    assert spec.delay_ms == 0


def test_mock_spec_custom_values():
    spec = MockSpec(url="/api", method="POST", status=201, body={"ok": True}, once=True, delay_ms=150)
    assert spec.method == "POST"
    assert spec.status == 201
    assert spec.body == {"ok": True}
    assert spec.once is True
    assert spec.delay_ms == 150
