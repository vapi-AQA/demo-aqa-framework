import pytest

from aqa.utils.retry import retry


def test_retry_does_not_retry_unexpected_exception():
    calls = []

    @retry(times=3, delay=0, exceptions=ValueError)
    def boom():
        calls.append(1)
        raise RuntimeError("other")

    with pytest.raises(RuntimeError):
        boom()
    assert len(calls) == 1


def test_retry_immediate_success():
    calls = []

    @retry(times=3, delay=0)
    def ok():
        calls.append(1)
        return 42

    assert ok() == 42
    assert len(calls) == 1


def test_retry_times_zero_calls_once():
    calls = []

    @retry(times=0)
    def ok():
        calls.append(1)
        return "ok"

    assert ok() == "ok"
    assert len(calls) == 1
