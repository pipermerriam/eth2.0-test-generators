import contextlib
import functools
import random


@contextlib.contextmanager
def random_seed(seed=0):
    original_state = random.getstate()
    try:
        random.seed(seed)
        yield
    finally:
        random.setstate(original_state)


def seed(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        with random_seed():
            return fn(*args, **kwargs)
    return inner


def get_random_bytes(length):
    return bytes(random.randint(0, 255) for _ in range(length))
