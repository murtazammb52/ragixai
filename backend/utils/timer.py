import time
import functools
from loguru import logger


def timed(label: str = ""):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            result = fn(*args, **kwargs)
            ms = (time.perf_counter() - t0) * 1000
            logger.debug(f"{label or fn.__name__} took {ms:.1f}ms")
            return result
        return wrapper
    return decorator


def elapsed_ms(start: float) -> float:
    return (time.perf_counter() - start) * 1000
