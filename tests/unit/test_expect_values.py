import pytest

from aqa.core.expect import expect


@pytest.mark.parametrize(
    "value,matcher",
    [
        (1, "to_be_number"),
        (1.5, "to_be_number"),
        ("text", "to_be_string"),
        (True, "to_be_boolean"),
        ([1, 2], "to_be_array"),
        ({"a": 1}, "to_be_object"),
    ],
)
def test_type_matchers_accept_valid_values(value, matcher):
    getattr(expect(value), matcher)()


@pytest.mark.parametrize(
    "value,matcher",
    [
        ("1", "to_be_number"),
        (True, "to_be_number"),
        (1, "to_be_string"),
        (1, "to_be_boolean"),
        ({"a": 1}, "to_be_array"),
        ([1], "to_be_object"),
    ],
)
def test_type_matchers_reject_invalid_values(value, matcher):
    with pytest.raises(AssertionError):
        getattr(expect(value), matcher)()
