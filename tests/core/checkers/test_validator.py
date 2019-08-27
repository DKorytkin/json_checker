import pytest

from json_checker.core.checkers import Validator, Or, OptionalKey, And
from json_checker.core.reports import Report


@pytest.mark.parametrize(
    "validator_data, soft, current_data, expected_result",
    [
        [lambda x: x > 1, True, 12, None],
        [lambda x: x > 1, False, 12, None],
        [lambda x: x > 1, True, -12, "function error <lambda>"],
        [And(int, lambda x: x > 1), False, 12, None],
        [And(str, lambda x: x in ("1", "2")), False, "2", None],
        [And(int, bool), False, True, None],
        [Or(int, None), False, 12, None],
        [Or(int, None), False, None, None],
        [Or(str, lambda x: isinstance(type(x), type)), False, 12, None],
        [{OptionalKey("key"): "value"}, False, {"key": "value"}, None],
        [None, True, None, None],
        [None, True, 12, "current value 12 (int) is not None"],
        [{"test": And(int, lambda x: x > 1)}, True, {"test": 666}, None],
        [{"test": Or(int, None)}, True, {"test": None}, None],
        [{"test": int}, True, {"test": 666}, None],
        [{"test": int}, False, {"test": 666}, None],
        [{"test": [int]}, False, {"test": [1, 2, 3]}, None],
        [{"test": {"test2": int}}, True, {"test": {"test2": 2}}, None],
        [[int], False, [1, 2, 3], None],
        [[str], True, ["1", "2", "3"], None],
        [[int], False, [True], None],
        [[bool], False, [True, False, True], None],
        [[object], False, [12, False, True, "test"], None],
        [
            [{"test1": int, "test2": str, "test3": bool}],
            False,
            [{"test1": 666, "test2": "22", "test3": False}],
            None,
        ],
        [int, True, 123, None],
        [123, True, 123, None],
        ["test", True, "test", None],
        [int, True, "123", "current value '123' (str) is not int"],
        [int, False, 123, None],
        [int, False, True, None],
        [bool, False, True, None],
        [str, False, "1", None],
        [str, True, 1, "current value 1 (int) is not str"],
        ["test", False, "test", None],
        [1, False, 1, None],
    ],
)
def test_validator_positive(
    validator_data, soft, current_data, expected_result
):
    validator = Validator(
        validator_data, soft=soft, ignore_extra_keys=False, report=Report(soft)
    )
    assert validator.validate(current_data) == expected_result


def test_validator_some_dicts():
    soft = False
    checker = Validator(
        expected_data=Or({"key1": int}, {"key2": str}),
        soft=soft,
        report=Report(soft),
        ignore_extra_keys=False,
    )
    result = checker.validate({"key2": 12})
    assert result == 'From key="key2": \n\tcurrent value 12 (int) is not str'


@pytest.mark.parametrize(
    "validator_data, current_data, expected_result",
    (
        (
            And(int, lambda x: x > 1),
            -12,
            "Not valid data: current value -12 (int) is not And(int, <lambda>) (And)",
        ),
        (
            Or(int, None),
            "12",
            "Not valid data: current value '12' (str) is not Or(int, None) (Or)",
        ),
        (
            {OptionalKey("key"): "value"},
            {"key2": "value2"},
            "Missing keys in expected schema: key2",
        ),
        (
            {"key": "value"},
            {"key2": "value2"},
            "Missing keys in current response: key\nMissing keys in expected schema: key2",
        ),
        ({}, {"key2": "value2"}, "Missing keys in expected schema: key2"),
        (
            {"key": "value"},
            {"key": "value", "key2": "value2"},
            "Missing keys in expected schema: key2",
        ),
        ({"key2": "value2"}, {}, "Missing keys in current response: key2"),
        (
            {"key": "value", "key2": "value2"},
            {"key": "value"},
            "Missing keys in current response: key2",
        ),
        (
            {"test": And(int, lambda x: x > 1)},
            {"test": -666},
            'From key="test": \n'
            "\tNot valid data: current value -666 (int) is not And(int, <lambda>) (And)",
        ),
        (
            {"test": Or(int, None)},
            {"test": "None"},
            'From key="test": \n'
            "\tNot valid data: current value 'None' (str) is not Or(int, None) (Or)",
        ),
        (
            {"test": int},
            {"test": "666"},
            "From key=\"test\": \n\tcurrent value '666' (str) is not int",
        ),
        (
            {"test": [str]},
            {"test": ["1", 2, "3"]},
            'From key="test": \n\tcurrent value 2 (int) is not str',
        ),
        (
            [str],
            [1, "2", 3],
            "current value 1 (int) is not str\ncurrent value 3 (int) is not str",
        ),
    ),
)
def test_validator_positive_message(
    validator_data, current_data, expected_result
):
    soft = True
    validator = Validator(
        validator_data, soft=soft, report=Report(soft), ignore_extra_keys=False
    )
    assert expected_result == validator.validate(current_data)


def test_exist_validators():
    soft = True
    v1 = Validator([1, 2], soft=soft, report=Report(soft))
    v2 = Validator([1, 2], soft=soft, report=Report(soft))
    assert v1._validators and v2._validators
    assert v1._validators == v2._validators
