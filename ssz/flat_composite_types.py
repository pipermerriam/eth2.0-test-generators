import itertools
import random

import ssz
from ssz.sedes import (
    boolean,
    Boolean,
    Container,
    List,
    UInt,
    Vector,
)

from _utils import seed
from renderers import (
    render_test_case,
    render_test,
)


UINT_SIZES = tuple(8 * 2**exponent for exponent in range(0, 6))  # 8, 16, ..., 256
NUM_RANDOM_LENGTHS = 16
MAX_RANDOM_LIST_LENGTH = 512
MAX_RANDOM_VECTOR_LENGTH = 512
MAX_RANDOM_CONTAINER_LENGTH = 32


def get_random_basic_value(sedes):
    if isinstance(sedes, Boolean):
        return random.choice((True, False))
    elif isinstance(sedes, UInt):
        return random.randint(0, 8**sedes.size)
    else:
        raise ValueError("Neither bool nor UInt")


def generate_flat_list_test_cases():
    tags = ("composite", "list", "flat")
    for element_sedes in (boolean,) + tuple(UInt(bit_size) for bit_size in UINT_SIZES):
        sedes = List(element_sedes)
        lengths = (
            0,
            1,
            256 // element_sedes.size - 1,
            256 // element_sedes.size,
        ) + tuple(
            random.randint(0, MAX_RANDOM_LIST_LENGTH)
            for _ in range(NUM_RANDOM_LENGTHS)
        )
        for length in lengths:
            value = tuple(get_random_basic_value(element_sedes) for _ in range(length))
            yield render_test_case(
                sedes=sedes,
                valid=True,
                value=value,
                serial=ssz.encode(value, sedes),
                tags=tags,
            )


def generate_flat_homogenous_container_test_cases():
    tags = ("composite", "container", "flat", "homogenous")

    for element_sedes in (boolean,) + tuple(UInt(bit_size) for bit_size in UINT_SIZES):
        lengths = (
            0,
            1,
        ) + tuple(
            random.randint(0, MAX_RANDOM_CONTAINER_LENGTH)
            for _ in range(NUM_RANDOM_LENGTHS)
        )
        for length in lengths:
            fields = tuple(itertools.repeat(element_sedes, length))
            sedes = Container(fields)
            value = tuple(
                get_random_basic_value(element_sedes)
                for element_sedes in fields
            )
            yield render_test_case(
                sedes=sedes,
                valid=True,
                value=value,
                serial=ssz.encode(value, sedes),
                tags=tags,
            )


def generate_flat_heterogenous_container_test_cases():
    tags = ("composite", "container", "flat", "heterogenous")

    lengths = tuple(
        random.randint(0, MAX_RANDOM_CONTAINER_LENGTH)
        for _ in range(NUM_RANDOM_LENGTHS)
    )
    element_sedes_choices = (
        boolean,
    ) + tuple(
        UInt(bit_size) for bit_size in UINT_SIZES
    )
    for length in lengths:
        fields = tuple(random.choice(element_sedes_choices) for _ in range(length))
        sedes = Container(fields)
        value = tuple(
            get_random_basic_value(field)
            for field in fields
        )

        yield render_test_case(
            sedes=sedes,
            valid=True,
            value=value,
            serial=ssz.encode(value, sedes),
            tags=tags,
        )


def generate_flat_vector_test_cases():
    tags = ("composite", "vector", "flat", "homogenous")

    for element_sedes in (boolean,) + tuple(UInt(bit_size) for bit_size in UINT_SIZES):
        lengths = (
            0,
            1,
        ) + tuple(
            random.randint(0, MAX_RANDOM_VECTOR_LENGTH)
            for _ in range(NUM_RANDOM_LENGTHS)
        )
        for length in lengths:
            sedes = Vector(element_sedes, length)
            value = tuple(get_random_basic_value(element_sedes) for _ in range(length))
            yield render_test_case(
                sedes=sedes,
                valid=True,
                value=value,
                serial=ssz.encode(value, sedes),
                tags=tags,
            )


@seed
def generate_flat_list_test():
    return render_test(
        title="Flat List",
        summary="Tests for lists of basic types",
        version="0.1",
        test_cases=generate_flat_list_test_cases(),
    )


@seed
def generate_flat_container_test():
    return render_test(
        title="Flat Container",
        summary="Tests for containers consisting of only basic types",
        version="0.1",
        test_cases=itertools.chain(
            generate_flat_homogenous_container_test_cases(),
            generate_flat_heterogenous_container_test_cases(),
        )
    )


@seed
def generate_flat_vector_test():
    return render_test(
        title="Flat Vector",
        summary="Tests for vectors of basic types",
        version="0.1",
        test_cases=generate_flat_vector_test_cases(),
    )
