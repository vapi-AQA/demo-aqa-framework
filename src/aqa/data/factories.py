"""Seeded, reproducible test data (Faker) + small domain factories."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any

from faker import Faker


@dataclass(frozen=True, slots=True)
class User:
    name: str
    email: str
    phone: str
    password: str
    city: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class DataFactory:
    """One instance per test; seed comes from Settings so failures are reproducible."""

    def __init__(self, seed: int = 42, locale: str = "ru_RU"):
        self.seed = seed
        self.fake = Faker(locale)
        self.fake.seed_instance(seed)

    def user(self, **overrides: Any) -> User:
        payload = {
            "name": self.fake.name(),
            "email": self.fake.email(),
            "phone": self.fake.phone_number(),
            "password": self.fake.password(length=14),
            "city": self.fake.city(),
        }
        payload.update(overrides)
        return User(**payload)

    def payload(self, schema: dict[str, Callable[[Faker], Any]]) -> dict[str, Any]:
        """Generic builder: {'field': lambda faker: faker.*()}."""
        return {key: generator(self.fake) for key, generator in schema.items()}

    def email(self, domain: str = "example.com") -> str:
        return f"{self.fake.user_name()}.{self.fake.random_number(digits=6)}@{domain}"
