from aqa.data.factories import DataFactory, User


def test_seed_reproducibility():
    first = DataFactory(seed=123).user()
    second = DataFactory(seed=123).user()
    assert first == second


def test_different_seeds_produce_different_users():
    first = DataFactory(seed=1).user()
    second = DataFactory(seed=2).user()
    assert first != second


def test_user_factory_and_overrides():
    user = DataFactory(seed=7).user(email="fixed@example.com", city="TestCity")
    assert isinstance(user, User)
    assert user.email == "fixed@example.com"
    assert user.city == "TestCity"
    assert user.password
    assert user.as_dict()["email"] == "fixed@example.com"


def test_generic_payload_builder():
    payload = DataFactory(seed=1).payload(
        {"login": lambda faker: faker.user_name(), "age": lambda faker: faker.random_int(18, 60)}
    )
    assert set(payload) == {"login", "age"}
    assert 18 <= payload["age"] <= 60
    assert isinstance(payload["login"], str)


def test_email_helper():
    email = DataFactory(seed=5).email(domain="test.local")
    assert email.endswith("@test.local")
