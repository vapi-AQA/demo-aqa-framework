import pytest

from aqa.api.schema import iter_schema_errors, validate_schema

SCHEMA = {
    "type": "object",
    "properties": {"id": {"type": "integer"}, "email": {"type": "string", "format": "email"}},
    "required": ["id", "email"],
}


def test_valid_payload_passes():
    validate_schema({"id": 1, "email": "user@example.com"}, SCHEMA)


def test_invalid_payload_raises_with_details():
    with pytest.raises(AssertionError, match="Schema validation failed"):
        validate_schema({"id": "one"}, SCHEMA)
    assert iter_schema_errors({"id": "one", "email": "bad"}, SCHEMA)
