import random

from eth_utils import (
    to_tuple,
)

import ssz
from ssz.sedes import (
    UInt,
)

from _utils import (
    seed,
    get_random_bytes,
)
from renderers import (
    render_test,
    render_test_case,
)


BIT_SIZES = [i for i in range(8, 512 + 1, 8)]
RANDOM_TEST_CASES_PER_BIT_SIZE = 10
RANDOM_TEST_CASES_PER_LENGTH = 3


@seed
def generate_uint_bounds_test():
    test_cases = generate_uint_bounds_test_cases() + generate_uint_out_of_bounds_test_cases()

    return render_test(
        title="UInt Bounds",
        summary="Integers right at or beyond the bounds of the allowed value range",
        fork="phase0-0.2.0",
        test_cases=test_cases,
    )


@seed
def generate_uint_random_test():
    test_cases = generate_random_uint_test_cases()

    return render_test(
        title="UInt Random",
        summary="Random integers chosen uniformly over the allowed value range",
        fork="phase0-0.2.0",
        test_cases=test_cases,
    )


@seed
def generate_uint_wrong_length_test():
    test_cases = generate_uint_wrong_length_test_cases()

    return render_test(
        title="UInt Wrong Length",
        summary="Serialized integers that are too short or too long",
        fork="phase0-0.2.0",
        test_cases=test_cases,
    )


@to_tuple
def generate_random_uint_test_cases():
    tags = ("atomic", "uint", "random")

    for bit_size in BIT_SIZES:
        sedes = UInt(bit_size)

        for _ in range(RANDOM_TEST_CASES_PER_BIT_SIZE):
            value = random.randrange(0, 2 ** bit_size)
            serial = ssz.encode(value, sedes)
            yield render_test_case(
                sedes=sedes,
                valid=True,
                value=value,
                serial=serial,
                tags=tags,
            )


@to_tuple
def generate_uint_wrong_length_test_cases():
    tags = ("atomic", "uint", "wrong_length")

    for bit_size in BIT_SIZES:
        sedes = UInt(bit_size)
        lengths = sorted({
            0,
            sedes.length // 2,
            sedes.length - 1,
            sedes.length + 1,
            sedes.length * 2,
        })
        for length in lengths:
            for _ in range(RANDOM_TEST_CASES_PER_LENGTH):
                yield render_test_case(
                    sedes=sedes,
                    valid=False,
                    serial=get_random_bytes(length),
                    tags=tags,
                )


@to_tuple
def generate_uint_bounds_test_cases():
    common_tags = ("atomic", "uint")
    for bit_size in BIT_SIZES:
        sedes = UInt(bit_size)

        for value, tag in ((0, "uint_lower_bound"), (2 ** bit_size - 1, "uint_upper_bound")):
            serial = ssz.encode(value, sedes)
            yield render_test_case(
                sedes=sedes,
                valid=True,
                value=value,
                serial=serial,
                tags=common_tags + (tag,),
            )


@to_tuple
def generate_uint_out_of_bounds_test_cases():
    common_tags = ("atomic", "uint")
    for bit_size in BIT_SIZES:
        sedes = UInt(bit_size)

        for value, tag in ((-1, "uint_underflow"), (2 ** bit_size, "uint_overflow")):
            yield render_test_case(
                sedes=sedes,
                valid=False,
                value=value,
                tags=common_tags + (tag,),
            )
