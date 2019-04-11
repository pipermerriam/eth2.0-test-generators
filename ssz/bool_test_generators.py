from eth_utils import (
    to_tuple,
)

import ssz
from ssz.sedes import (
    Boolean,
)
from renderers import (
    render_test,
    render_test_case,
)
from _utils import (
    seed,
)



@seed
def generate_bool_true_and_false_test():
    test_cases = mk_bool_true_and_false_test_cases()

    return render_test(
        title="Bool Values",
        summary="The two valid values for a boolean",
        fork="phase0-0.2.0",
        test_cases=test_cases,
    )


@seed
def generate_bool_wrong_length_test():
    test_cases = mk_bool_wrong_length_test_cases()

    return render_test(
        title="Bool Wrong Length",
        summary="Byte strings of incorrect length",
        fork="phase0-0.2.0",
        test_cases=test_cases,
    )


@seed
def generate_bool_invalid_byte_test():
    test_cases = mk_bool_invalid_byte_test_cases()

    return render_test(
        title="Bool Invalid Byte",
        summary="Single byte values that are not 0x00 or 0x01",
        fork="phase0-0.2.0",
        test_cases=test_cases,
    )


@to_tuple
def mk_bool_true_and_false_test_cases():
    sedes = Boolean()

    true_serial = ssz.encode(True, sedes)
    yield render_test_case(
        sedes=sedes,
        valid=True,
        value=True,
        serial=true_serial,
        tags=("atomic", "bool", "true")
    )

    false_serial = ssz.encode(False, sedes)
    yield render_test_case(
        sedes=sedes,
        valid=True,
        value=False,
        serial=false_serial,
        tags=("atomic", "bool", "false")
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


@to_tuple
def mk_bool_wrong_length_test_cases():
    tags = ("atomic", "bool", "wrong_length")
    sedes = Boolean()

    for serial in WRONG_LENGTH_SERIALS:
        yield render_test_case(
            sedes=sedes,
            valid=False,
            serial=serial,
            tags=tags,
        )


@to_tuple
def mk_bool_invalid_byte_test_cases():
    tags = ("atomic", "bool", "invalid")
    sedes = Boolean()

    for i in range(2, 255):
        serial = bytes((i,))
        yield render_test_case(
            sedes=sedes,
            valid=False,
            serial=serial,
            tags=tags,
        )
