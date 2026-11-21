import pytest

from aqa.config import Settings


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("AQA_BASE_URL", "https://example.org/")
    monkeypatch.setenv("AQA_SEED", "777")
    monkeypatch.setenv("AQA_LOGIN", "user")
    monkeypatch.setenv("AQA_PASSWORD", "secret")

    settings = Settings.from_env()
    assert settings.base_url == "https://example.org/"
    assert settings.seed == 777
    assert settings.credentials


def test_environment_info_hides_secrets():
    info = Settings.from_env().environment_info()
    assert "credentials.login" not in info
    assert "credentials.password" not in info
    assert "credentials.provided" in info


def test_malformed_int_env_raises(monkeypatch):
    monkeypatch.setenv("AQA_SEED", "not-a-number")
    with pytest.raises(ValueError):
        Settings.from_env()
