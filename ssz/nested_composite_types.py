import random
from functools import (
    partial,
)
from itertools import (
    product,
)

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
NUM_TEST_CASES_PER_TYPE = 20
MAX_RANDOM_LIST_LENGTH = 16
MAX_RANDOM_VECTOR_LENGTH = 16
MAX_RANDOM_CONTAINER_LENGTH = 8

NUM_DEEP_NESTING_TEST_CASES = 20
DEEP_NESTING_MAX_WIDTH = 4
DEEP_NESTING_EXPECTED_BRANCH_LENGTH = 4
# choose to go one layer deeper with this probability
DEEP_NESTING_NEXT_LAYER_PROB = 1 - 1 / DEEP_NESTING_EXPECTED_BRANCH_LENGTH


def get_random_vector_length():
    return random.randint(0, MAX_RANDOM_VECTOR_LENGTH)


def get_random_basic_sedes():
    return random.choice((
        boolean,
    ) + tuple(
        UInt(bit_size)
        for bit_size in UINT_SIZES
    ))


def get_random_value(sedes, max_list_length):
    if isinstance(sedes, Boolean):
        return random.choice((True, False))
    elif isinstance(sedes, UInt):
        return random.randint(0, 8**sedes.size)
    elif isinstance(sedes, Vector):
        return tuple(
            get_random_value(sedes.element_sedes, max_list_length)
            for _ in range(sedes.length)
        )
    elif isinstance(sedes, List):
        length = random.randint(0, max_list_length)
        return tuple(
            get_random_value(sedes.element_sedes, max_list_length)
            for _ in range(length)
        )
    elif isinstance(sedes, Container):
        return tuple(
            get_random_value(field, max_list_length)
            for field in sedes.field_sedes
        )
    else:
        raise ValueError(f"Cannot generate random value for sedes {sedes}")


def get_random_list_sedes(element_sedes_factory):
    element_sedes = element_sedes_factory()
    return List(element_sedes)


def get_random_vector_sedes(element_sedes_factory, max_length):
    length = random.randint(0, max_length)
    element_sedes = element_sedes_factory()
    return Vector(element_sedes, length)


def get_random_container_sedes(element_sedes_factory, max_length):
    length = random.randint(0, max_length)
    fields = tuple(
        element_sedes_factory()
        for index in range(length)
    )
    return Container(fields)


def get_random_deep_nested_sedes():
    should_go_deeper = random.random() < DEEP_NESTING_NEXT_LAYER_PROB

    composite_sedes_factories = tuple((
        get_random_list_sedes,
        partial(get_random_vector_sedes, max_length=DEEP_NESTING_MAX_WIDTH),
        partial(get_random_container_sedes, max_length=DEEP_NESTING_MAX_WIDTH),
    ))

    if not should_go_deeper:
        return get_random_basic_sedes()

    else:
        sedes_factory = random.choice(composite_sedes_factories)
        return sedes_factory(get_random_deep_nested_sedes)


def generate_two_layer_composite_test_cases():
    tags = ("composite", "nested", "shallow")

    composite_sedes_factories = tuple((
        get_random_list_sedes,
        partial(get_random_vector_sedes, max_length=MAX_RANDOM_VECTOR_LENGTH),
        partial(get_random_container_sedes, max_length=MAX_RANDOM_VECTOR_LENGTH),
    ))

    inner_sedes_factories = tuple(
        partial(sedes_factory, get_random_basic_sedes)
        for sedes_factory in composite_sedes_factories
    )
    inner_and_outer_sedes_factories = product(inner_sedes_factories, composite_sedes_factories)
    for inner_sedes_factory, outer_sedes_factory in inner_and_outer_sedes_factories:
        for _ in range(NUM_TEST_CASES_PER_TYPE):
            outer_sedes = outer_sedes_factory(inner_sedes_factory)

            value = get_random_value(outer_sedes, max_list_length=MAX_RANDOM_LIST_LENGTH)
            yield render_test_case(
                sedes=outer_sedes,
                valid=True,
                value=value,
                serial=ssz.encode(value, outer_sedes),
                tags=tags,
            )


def generate_deeply_nested_composite_test_cases():
    tags = ("composite", "nested", "deep")

    for _ in range(NUM_DEEP_NESTING_TEST_CASES):
        sedes = get_random_deep_nested_sedes()
        value = get_random_value(sedes, DEEP_NESTING_MAX_WIDTH)
        yield render_test_case(
            sedes=sedes,
            valid=True,
            value=value,
            serial=ssz.encode(value, sedes),
            tags=tags,
        )


@seed
def generate_two_layer_composite_test():
    return render_test(
        title="Nested composite types",
        summary="Tests for composite types of other composite types",
        version="0.1",
        test_cases=generate_two_layer_composite_test_cases(),
    )


@seed
def generate_deeply_nested_composite_test():
    return render_test(
        title="Deeply nested composite types",
        summary="Tests for nested composite types with a random number of layers",
        version="0.1",
        test_cases=generate_deeply_nested_composite_test_cases(),
    )
