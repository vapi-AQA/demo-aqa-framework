from aqa.config import Credentials, Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.base_url
    assert settings.default_timeout_ms > 0
    assert settings.seed == 42


def test_credentials_bool():
    assert not Credentials()
    assert not Credentials(login="u")
    assert not Credentials(password="p")
    assert Credentials(login="u", password="p")


def test_credentials_from_env(monkeypatch):
    monkeypatch.setenv("AQA_LOGIN", "qa")
    monkeypatch.setenv("AQA_PASSWORD", "secret")
    creds = Credentials.from_env()
    assert creds.login == "qa"
    assert creds.password == "secret"
    assert bool(creds) is True


def test_settings_env_overrides(monkeypatch):
    monkeypatch.setenv("AQA_API_BASE_URL", "http://api.local")
    monkeypatch.setenv("AQA_LOCALE", "en-US")
    settings = Settings.from_env()
    assert settings.api_base_url == "http://api.local"
    assert settings.locale == "en-US"
