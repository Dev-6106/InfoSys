import time
from functools import wraps
from loguru import logger

def rate_limit(min_interval_sec: float):
    def deco(fn):
        last = {"t": 0.0}
        @wraps(fn)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last["t"]
            if elapsed < min_interval_sec:
                time.sleep(min_interval_sec - elapsed)
            res = fn(*args, **kwargs)
            last["t"] = time.time()
            return res
        return wrapper
    return deco

def log_calls(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper
