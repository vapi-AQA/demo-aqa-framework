"""Configuration via environment variables.

Все настройки собираются в один immutable-объект `Settings` и передаются
фикстурами - тесты не читают `os.getenv` напрямую.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _env_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


@dataclass(frozen=True, slots=True)
class Credentials:
    login: str = ""
    password: str = ""

    @classmethod
    def from_env(cls) -> Credentials:
        return cls(login=os.getenv("AQA_LOGIN", ""), password=os.getenv("AQA_PASSWORD", ""))

    def __bool__(self) -> bool:
        return bool(self.login and self.password)


@dataclass(frozen=True, slots=True)
class Settings:
    base_url: str = "https://playwright.dev/"
    api_base_url: str = ""
    default_timeout_ms: int = 15_000
    navigation_timeout_ms: int = 30_000
    viewport_width: int = 1440
    viewport_height: int = 900
    locale: str = "ru-RU"
    seed: int = 42
    credentials: Credentials = field(default_factory=Credentials)
    artifacts_dir: Path = Path("artifacts")

    @classmethod
    def from_env(cls) -> Settings:
        defaults = cls()  # dataclass defaults resolved correctly
        return cls(
            base_url=os.getenv("AQA_BASE_URL", defaults.base_url),
            api_base_url=os.getenv("AQA_API_BASE_URL", defaults.api_base_url),
            default_timeout_ms=_env_int("AQA_DEFAULT_TIMEOUT_MS", defaults.default_timeout_ms),
            navigation_timeout_ms=_env_int("AQA_NAVIGATION_TIMEOUT_MS", defaults.navigation_timeout_ms),
            viewport_width=_env_int("AQA_VIEWPORT_WIDTH", defaults.viewport_width),
            viewport_height=_env_int("AQA_VIEWPORT_HEIGHT", defaults.viewport_height),
            locale=os.getenv("AQA_LOCALE", defaults.locale),
            seed=_env_int("AQA_SEED", defaults.seed),
            credentials=Credentials.from_env(),
            artifacts_dir=Path(os.getenv("AQA_ARTIFACTS_DIR", str(defaults.artifacts_dir))),
        )

    def environment_info(self) -> dict[str, str]:
        """Для Allure environment.properties."""
        skip = {"credentials", "artifacts_dir"}
        info = {}
        for item in fields(self):
            if item.name in skip:
                continue
            value = getattr(self, item.name)
            info[item.name] = str(value)
        info["credentials.provided"] = str(bool(self.credentials))
        return info
