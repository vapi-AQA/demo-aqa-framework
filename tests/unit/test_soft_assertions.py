import pytest

from aqa.core.expect import soft_assert


def test_soft_assert_collects_failures():
    with pytest.raises(AssertionError) as exc, soft_assert() as verify:
        verify.check(False, "first failure")
        verify.check(True, "ok")
        verify.check(False, "second failure")
    message = str(exc.value)
    assert "1) first failure" in message
    assert "2) second failure" in message


def test_soft_assert_passes_without_failures():
    with soft_assert() as verify:
        verify.check(True, "ok")
    assert not verify.failures


def test_soft_assert_manual_failure_list():
    verify = soft_assert()
    verify.failures.append("custom")
    with pytest.raises(AssertionError, match="1\\) custom"):
        verify.__exit__(None, None, None)
