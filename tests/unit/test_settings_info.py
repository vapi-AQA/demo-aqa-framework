from pathlib import Path

from aqa.config import Settings


def test_environment_info_contains_expected_keys():
    settings = Settings(base_url="https://x.test/", api_base_url="https://api.test/")
    info = settings.environment_info()
    assert info["base_url"] == "https://x.test/"
    assert info["api_base_url"] == "https://api.test/"
    assert info["seed"] == "42"
    assert info["credentials.provided"] == "False"


def test_artifacts_dir_default_type():
    settings = Settings()
    assert isinstance(settings.artifacts_dir, Path)
