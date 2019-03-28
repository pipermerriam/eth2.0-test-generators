from itertools import chain
from random import Random

import ssz
from ssz.sedes import (
    boolean,
    Boolean,
    Container,
    List,
    UInt,
    Vector,
)

from renderers import (
    render_test_case,
    render_test,
)


random = Random(0)

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
                tags=["composite", "list", "flat"],
            )


def generate_flat_homogenous_container_test_cases():
    for element_sedes in (boolean,) + tuple(UInt(bit_size) for bit_size in UINT_SIZES):
        lengths = (
            0,
            1,
        ) + tuple(
            random.randint(0, MAX_RANDOM_CONTAINER_LENGTH)
            for _ in range(NUM_RANDOM_LENGTHS)
        )
        for length in lengths:
            field_names = tuple(f"field{field_index}" for field_index in range(length))
            sedes = Container(tuple(
                (field_name, element_sedes)
                for field_name in field_names
            ))
            value = {
                field_name: get_random_basic_value(element_sedes)
                for field_name in field_names
            }
            yield render_test_case(
                sedes=sedes,
                valid=True,
                value=value,
                serial=ssz.encode(value, sedes),
                tags=["composite", "container", "flat", "homogenous"],
            )


def generate_flat_heterogenous_container_test_cases():
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
        field_names = tuple(f"field{field_index}" for field_index in range(length))
        field_sedes = tuple(random.choice(element_sedes_choices) for _ in range(length))
        sedes = Container(tuple(
            (field_name, field_sedes)
            for field_name, field_sedes in zip(field_names, field_sedes)
        ))
        value = {
            field_name: get_random_basic_value(sedes)
            for field_name, sedes in zip(field_names, field_sedes)
        }

        yield render_test_case(
            sedes=sedes,
            valid=True,
            value=value,
            serial=ssz.encode(value, sedes),
            tags=["composite", "container", "flat", "heterogenous"],
        )


def generate_flat_vector_test_cases():
    for element_sedes in (boolean,) + tuple(UInt(bit_size) for bit_size in UINT_SIZES):
        lengths = (
            0,
            1,
        ) + tuple(
            random.randint(0, MAX_RANDOM_VECTOR_LENGTH)
            for _ in range(NUM_RANDOM_LENGTHS)
        )
        for length in lengths:
            sedes = Vector(length, element_sedes)
            value = tuple(get_random_basic_value(element_sedes) for _ in range(length))
            yield render_test_case(
                sedes=sedes,
                valid=True,
                value=value,
                serial=ssz.encode(value, sedes),
                tags=["composite", "vector", "flat", "homogenous"],
            )


def generate_flat_list_test():
    return render_test(
        title="Flat List",
        summary="Tests for lists of basic types",
        version="0.1",
        test_cases=generate_flat_list_test_cases(),
    )


def generate_flat_container_test():
    return render_test(
        title="Flat Container",
        summary="Tests for containers consisting of only basic types",
        version="0.1",
        test_cases=chain(
            generate_flat_homogenous_container_test_cases(),
            generate_flat_heterogenous_container_test_cases(),
        )
    )


def generate_flat_vector_test():
    return render_test(
        title="Flat Vector",
        summary="Tests for vectors of basic types",
        version="0.1",
        test_cases=generate_flat_vector_test_cases(),
    )
