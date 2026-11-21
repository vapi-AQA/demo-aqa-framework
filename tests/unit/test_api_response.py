from aqa.api.client import ApiResponse


def test_api_response_json_and_fields():
    response = ApiResponse(status=200, headers={"content-type": "application/json"}, body=b'{"id":1}', data={"id": 1})
    assert response.status == 200
    assert response.json() == {"id": 1}
    assert response.headers["content-type"] == "application/json"
    assert response.body == b'{"id":1}'


def test_api_response_with_text_data():
    response = ApiResponse(status=200, headers={}, body=b"ok", data="ok")
    assert response.json() == "ok"
