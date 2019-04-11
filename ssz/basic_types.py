import itertools
import random

import ssz
from ssz.sedes import (
    boolean,
    UInt,
)

from _utils import seed
from renderers import (
    render_test_case,
    render_test,
)

UINT_SIZES = tuple(8 * 2**exponent for exponent in range(0, 6))  # 8, 16, ..., 256
NUM_RANDOM_UINT_VALUES = 16


def generate_uint_test_cases():
    tags = ("basic", "uint")

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
                tags=tags,
            )


@seed
def generate_uint_test():
    return render_test(
        title="UInt",
        summary="UInt tests for all sizes",
        version="0.1",
        test_cases=generate_uint_test_cases(),
    )


def generate_bool_true_and_false_test_cases():
    tags = ("basic", "bool")
    for value in (True, False):
        yield render_test_case(
            sedes=boolean,
            valid=True,
            value=value,
            serial=ssz.encode(value, boolean),
            tags=tags,
        )


WRONG_LENGTH_SERIALS = (
    b'',
    b'\x00' * 2,
    b'\x01' * 2,
    b'\xFF' * 2,
    b'\x00' * 3,
    b'\x01' * 3,
    b'\xFF' * 3,
    b'\x00' * 5,
    b'\x01' * 5,
    b'\xFF' * 5,
    b'\x00\x01',
    b'\x01\x00',
    b'\x00\xFF',
    b'\x01\xFF',
)


def generate_bool_wrong_length_test_cases():
    tags = ("atomic", "bool", "wrong_length")
    sedes = boolean

    for serial in WRONG_LENGTH_SERIALS:
        yield render_test_case(
            sedes=sedes,
            valid=False,
            serial=serial,
            tags=tags,
        )


def generate_bool_invalid_byte_test_cases():
    tags = ("atomic", "bool", "invalid")
    sedes = boolean

    for i in range(2, 255):
        serial = bytes((i,))
        yield render_test_case(
            sedes=sedes,
            valid=False,
            serial=serial,
            tags=tags,
        )


@seed
def generate_bool_test():
    return render_test(
        title="Bool",
        summary="Tests for the two bool values",
        version="0.1",
        test_cases=itertools.chain(
            generate_bool_true_and_false_test_cases(),
            generate_bool_wrong_length_test_cases(),
            generate_bool_invalid_byte_test_cases(),
        ),
    )
