from collections.abc import (
    Mapping,
    Sequence,
)

from eth_utils import (
    encode_hex,
    to_dict,
)

from ssz.sedes import (
    BaseSedes,
    Boolean,
    Container,
    List,
    UInt,
    Vector,
)


def render_value(value):
    if isinstance(value, bool):
        return value
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, bytes):
        return encode_hex(value)
    elif isinstance(value, Sequence):
        return tuple(render_value(element) for element in value)
    elif isinstance(value, Mapping):
        return render_dict_value(value)
    else:
        raise ValueError(f"Cannot render value {value}")


@to_dict
def render_dict_value(value):
    for key, value in value.items():
        yield key, render_value(value)


def render_type_definition(sedes):
    if isinstance(sedes, Boolean):
        return "bool"

    elif isinstance(sedes, UInt):
        return f"uint{sedes.size * 8}"

    elif isinstance(sedes, Vector):
        return [render_type_definition(sedes.element_sedes), sedes.length]

    elif isinstance(sedes, List):
        return [render_type_definition(sedes.element_sedes)]

    elif isinstance(sedes, Container):
        return tuple(
            render_type_definition(field)
            for field in sedes.field_sedes
        )

    elif isinstance(sedes, BaseSedes):
        raise Exception("Unreachable: All sedes types have been checked")

    else:
        raise TypeError("Expected BaseSedes")


@to_dict
def render_test_case(*, sedes, valid, value=None, serial=None, description=None, tags=None):
    value_and_serial_given = value is not None and serial is not None
    if valid:
        if not value_and_serial_given:
            raise ValueError("For valid test cases, both value and ssz must be present")
    else:
        if value_and_serial_given:
            raise ValueError("For invalid test cases, either value or ssz must not be present")

    if tags is None:
        tags = []

    # Ensure that ruemel doesn't use references, allowing callers of this
    # function to re-use the same `tags` object across multiple calls.
    tags = tuple(tag for tag in tags)

    yield "type", render_type_definition(sedes)
    yield "valid", valid
    if value is not None:
        yield "value", render_value(value)
    if serial is not None:
        yield "ssz", encode_hex(serial)
    if description is not None:
        yield description
    yield "tags", tags


@to_dict
def render_test(*, title, summary, version, test_cases):
    yield "title", title,
    if summary is not None:
        yield "summary", summary
    yield "version", version
    yield "test_cases", tuple(test_cases)
