from random import Random

import ssz
from ssz.sedes import (
    boolean,
    UInt,
)

from renderers import (
    render_test_case,
    render_test,
)


random = Random(0)

UINT_SIZES = tuple(8 * 2**exponent for exponent in range(0, 6))  # 8, 16, ..., 256
NUM_RANDOM_UINT_VALUES = 16


def generate_uint_test_cases():
    for bit_size in UINT_SIZES:
        sedes = UInt(bit_size)
        max_int = 2**bit_size - 1

        values = (
            0,
            1,
            max_int - 1,
            max_int,
        ) + tuple(
            random.randint(0, max_int) for _ in range(NUM_RANDOM_UINT_VALUES)
        )

        for value in values:
            serial = ssz.encode(value, sedes)
            yield render_test_case(
                sedes=sedes,
                valid=True,
                value=value,
                serial=serial,
                tags=["basic", "uint"],
            )


def generate_uint_test():
    return render_test(
        title="UInt",
        summary="UInt tests for all sizes",
        version="0.1",
        test_cases=generate_uint_test_cases(),
    )


def generate_bool_test_cases():
    for value in (True, False):
        yield render_test_case(
            sedes=boolean,
            valid=True,
            value=value,
            serial=ssz.encode(value, boolean),
            tags=["basic", "bool"],
        )


def generate_bool_test():
    return render_test(
        title="Bool",
        summary="Tests for the two bool values",
        version="0.1",
        test_cases=generate_bool_test_cases(),
    )
