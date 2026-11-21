"""JSON Schema contract validation with Allure attachments."""

from __future__ import annotations

from typing import Any

from jsonschema import Draft7Validator, FormatChecker
from jsonschema.exceptions import ValidationError

from aqa.core.steps import attach_json


def iter_schema_errors(instance: Any, schema: dict) -> list[ValidationError]:
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    return sorted(validator.iter_errors(instance), key=lambda e: list(e.path))


def validate_schema(instance: Any, schema: dict, name: str = "API response") -> None:
    errors = iter_schema_errors(instance, schema)
    attach_json({"schema": schema, "actual": instance}, name=f"{name}: schema check")
    if errors:
        details = [
            {
                "path": "/".join(str(p) for p in error.absolute_path) or "<root>",
                "message": error.message,
                "validator": error.validator,
            }
            for error in errors
        ]
        attach_json(details, name=f"{name}: validation errors")
        raise AssertionError(f"Schema validation failed for {name}: {details}")
