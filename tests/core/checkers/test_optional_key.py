import pytest

from json_checker.app import Checker
from json_checker.core.checkers import OptionalKey


# TODO need more tests for OptionalKey class


def test_create_optional_key_instance():
    o = OptionalKey("test_key")
    assert o.expected_data == "test_key"


def test_optional_key_str():
    op_key = OptionalKey("test_key")
    assert op_key.__str__() == "OptionalKey(test_key)"


def test_optional_key_string():
    assert str(OptionalKey("test_key")) == "OptionalKey(test_key)"


@pytest.mark.parametrize(
    "data",
    [
        [{OptionalKey("key"): "value"}, {"key": "value"}, {"key": "value"}],
        [{OptionalKey("key"): "value"}, {}, {}],
        [
            {OptionalKey("key"): "value", "key2": "value2"},
            {"key2": "value2"},
            {"key2": "value2"},
        ],
    ],
)
def test_operator_optional_key(data):
    optional_data, current_data, expected_result = data
    assert Checker(optional_data).validate(current_data) == expected_result
