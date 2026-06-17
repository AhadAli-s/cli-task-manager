"""
Lab 3 — Decorator Pattern
"""

import functools
import time
from typing import Callable, Any


def timing_decorator(func: Callable) -> Callable:
    """Measures and prints how long the decorated function took to execute."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[TIMING] {func.__name__} completed in {elapsed:.4f}s")
        return result

    return wrapper


def logging_decorator(func: Callable) -> Callable:
    """Logs the function name and arguments before execution."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        display_args = args[1:] if args and hasattr(args[0], '__dict__') else args
        print(f"[LOG] {func.__name__} called with args={display_args} kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            print(f"[LOG] {func.__name__} -> success")
            return result
        except Exception as exc:
            print(f"[LOG] {func.__name__} -> {type(exc).__name__}")
            raise

    return wrapper


def retry_decorator(max_retries: int = 3) -> Callable:
    """Retries the decorated function up to max_retries times on exception."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Exception | None = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if attempt < max_retries:
                        print(f"[RETRY] attempt {attempt + 1} of {max_retries}")
            raise last_exc  # type: ignore[misc]

        return wrapper

    return decorator


def make_cache() -> tuple[Callable, Callable]:
    """Return a matched pair of decorators that share one cache."""
    cache: dict[str, Any] = {}

    def cache_read(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self: Any, task_id: str, **kwargs: Any) -> Any:
            if task_id in cache:
                print(f"[CACHE] {func.__name__}: hit  for '{task_id}'")
                return cache[task_id]
            result = func(self, task_id, **kwargs)
            cache[task_id] = result
            print(f"[CACHE] {func.__name__}: stored '{task_id}'")
            return result
        return wrapper

    def cache_invalidate(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self: Any, task_or_id: Any, **kwargs: Any) -> Any:
            task_id = (
                task_or_id.get("id")
                if isinstance(task_or_id, dict)
                else task_or_id
            )
            if task_id and task_id in cache:
                del cache[task_id]
                print(f"[CACHE] {func.__name__}: invalidated '{task_id}'")
            return func(self, task_or_id, **kwargs)
        return wrapper

    return cache_read, cache_invalidate
