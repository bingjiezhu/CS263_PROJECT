"""Simple retry decorator with exponential backoff."""

from __future__ import annotations

import time
from typing import Callable, Tuple, Type


def retry(
    exceptions: Tuple[Type[BaseException], ...],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    backoff: float = 2.0,
):
    """Retry a function when it raises one of the provided exceptions."""

    def decorator(func: Callable):
        """Wrap a function with retry logic."""
        def wrapper(*args, **kwargs):
            """Execute the wrapped function with retries."""
            attempt = 1
            delay = base_delay
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt >= max_attempts:
                        raise
                    time.sleep(delay)
                    attempt += 1
                    delay *= backoff

        return wrapper

    return decorator
