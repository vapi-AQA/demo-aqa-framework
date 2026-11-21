from unittest.mock import MagicMock, patch

from aqa.core.steps import step


def test_step_preserves_name_and_return_value():
    @step("named step")
    def sample(x):
        """doc"""
        return x + 1

    assert sample.__name__ == "sample"
    assert sample.__doc__ == "doc"

    cm = MagicMock()
    cm.__enter__.return_value = None
    cm.__exit__.return_value = False
    with patch("aqa.core.steps.allure.step", return_value=cm) as mocked:
        assert sample(2) == 3
        mocked.assert_called_once_with("named step")


def test_step_formats_title_from_args():
    @step("open {path}")
    def open_page(path):
        return path

    cm = MagicMock()
    cm.__enter__.return_value = None
    cm.__exit__.return_value = False
    with patch("aqa.core.steps.allure.step", return_value=cm) as mocked:
        assert open_page("/demo") == "/demo"
        mocked.assert_called_once_with("open /demo")
