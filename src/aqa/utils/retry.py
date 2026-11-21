"""Small dependency-free retry decorator for flaky API calls."""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import Any

ExceptionFilter = type[Exception] | tuple[type[Exception], ...]


def retry(
    times: int = 3,
    delay: float = 0.2,
    backoff: float = 2.0,
    exceptions: ExceptionFilter = Exception,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if times < 1:
                return func(*args, **kwargs)
            pause = delay
            last_error: Exception | None = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as error:  # noqa: PERF203
                    last_error = error
                    if attempt == times:
                        break
                    time.sleep(pause)
                    pause *= backoff
            raise last_error  # type: ignore[misc]

        return wrapper

    return decorator
