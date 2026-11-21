# AQA Framework - Python-фреймворк для E2E/API-тестов

Один фреймворк с набором проверенных практик: POM, Allure, проверки, API-контракты, моки, данные, конфиг, CI.

## Используемые практики

| Практика | Где реализовано |
|---|---|
| **Configuration as code** (env → immutable `Settings`) | `src/aqa/config.py` |
| **DI через pytest fixtures** - тесты ничего не создают сами | `conftest.py` |
| **Page Object Model + Fragment + Component** | `pages/`, `src/aqa/core/` |
| **Один метод = один Allure-шаг** (`@step`) | `src/aqa/core/steps.py` |
| **Hard + soft assertions** (`expect`, `soft_assert`) | `src/aqa/core/expect.py` |
| **API-клиент с retry, схемами и контрактами** | `src/aqa/api/` |
| **Локальный HTTP-стенд для API-тестов** (без внешней сети) | `conftest.py::local_api` |
| **Сетевые моки как фикстура с автосбросом** | `src/aqa/mocks/api_mock.py` |
| **Воспроизводимые данные** (seeded Faker + фабрики) | `src/aqa/data/factories.py` |
| **Скриншот/видео/trace при падении** | `conftest.py` hooks |
| **Allure environment.properties + маркеры** | `pytest_configure`, `pyproject.toml` |
| **Secrets только из env** | `.env.example`, CI secrets |
| **Линт и параллельный прогон** | `ruff`, `pytest-xdist`, `Makefile`, `.github/workflows/ci.yml` |

## Структура

```
aqa-framework/
  src/aqa/
    config.py              Settings/Credentials из env
    core/                  Component, BasePage, expect/soft_assert, @step
    api/                   ApiClient + JSON Schema валидация
    mocks/                 ApiMock (page.route)
    data/                  DataFactory (seeded Faker)
    utils/retry.py         retry с экспоненциальной задержкой
  pages/playwright_site/   HeaderFragment, SearchDialogFragment, MainPage
  conftest.py              фикстуры + хуки отчётности
  tests/unit/              конфиг, retry, schema, data
  tests/e2e/               UI (live), API-контракты (offline), моки (live)
  .env.example, Makefile, .github/workflows/ci.yml
```

## Быстрый старт

```bash
cd aqa-framework
cp .env.example .env
make install
make test              # unit + API против локального сервера, без интернета
RUN_LIVE_TESTS=1 make report
```

Или напрямую:

```bash
pytest tests/unit tests/e2e/test_api_contract.py
RUN_LIVE_TESTS=1 pytest -n auto --alluredir=allure-results
allure serve allure-results
```

## Правила написания теста

1. Импортируй `expect`/`soft_assert`/`step` из `aqa`, страницы - из `pages`.
2. Селекторы - только внутри фрагмента/компонента, один раз.
3. Действие и проверка - разные методы; действий нет в `tests/`.
4. Для нескольких проверок одного экрана используй `with soft_assert() as verify:`.
5. Внешние запросы - только через `ApiClient`; моки - через `api_mock`.
6. Тест, требующий сети, помечай `@pytest.mark.live`.
7. Данные - через `DataFactory` (seed из `Settings`), а не `random` в тесте.

## Архитектурные решения

- Общие слои вынесены в `src/aqa` и не дублируются между проектами.
- API-тесты работают против встроенного HTTP-сервера: офлайн-часть прогона детерминирована.
- Soft assertions, `@step` с автоподстановкой имени, retry, env-конфиг, линтер, CI и авто-environment для Allure.
- Настройки и секреты разделены; живые тесты включаются явно.
