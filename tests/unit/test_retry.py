import pytest

from aqa.utils.retry import retry


def test_retry_succeeds_on_third_attempt():
    calls = []

    @retry(times=3, delay=0, exceptions=ValueError)
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ValueError("flaky")
        return "ok"

    assert flaky() == "ok"
    assert len(calls) == 3


def test_retry_gives_up():
    calls = []

    @retry(times=2, delay=0, exceptions=ValueError)
    def always_fails():
        calls.append(1)
        raise ValueError("nope")

    with pytest.raises(ValueError):
        always_fails()
    assert len(calls) == 2
