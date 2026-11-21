import pytest

from aqa.api.schema import iter_schema_errors, validate_schema

USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "email": {"type": "string", "format": "email"},
        "role": {"type": "string", "enum": ["admin", "member"]},
    },
    "required": ["id", "email"],
}


def test_schema_allows_optional_fields():
    validate_schema({"id": 1, "email": "a@b.com", "role": "admin"}, USER_SCHEMA)


def test_schema_reports_missing_required():
    errors = iter_schema_errors({"email": "a@b.com"}, USER_SCHEMA)
    assert errors
    assert any(error.validator == "required" for error in errors)


def test_schema_reports_wrong_type():
    errors = iter_schema_errors({"id": "1", "email": "a@b.com"}, USER_SCHEMA)
    assert any("id" in "/".join(map(str, e.path)) or e.validator == "type" for e in errors)


def test_validate_schema_attaches_and_raises():
    with pytest.raises(AssertionError):
        validate_schema({"id": 1}, USER_SCHEMA, name="user payload")
