import pytest

from json_checker.core.checkers import And


def test_create_and_instance():
    a = And(int, str)
    assert a.expected_data == (int, str)


def test_create_and_instance_with_empty_param():
    a = And()
    assert a.expected_data == tuple()


def test_and_operator_string():
    assert str(And(int, None)) == "And(int, None)"


@pytest.mark.parametrize(
    "schema, current_data", [[(int, lambda x: x > 0), 1], [(int, bool), True]]
)
def test_operator_and(schema, current_data):
    assert And(*schema).validate(current_data) == ""


@pytest.mark.parametrize(
    "and_data, current_data, error_message",
    [
        [
            (int, bool),
            0,
            "Not valid data: "
            "current value 0 (int) is not And(int, bool) (And)",
        ],
        [
            (int, lambda x: x > 0),
            0,
            "Not valid data: "
            "current value 0 (int) is not And(int, <lambda>) (And)",
        ],
        [
            (int, lambda x: x > 0),
            "1",
            "Not valid data: "
            "current value '1' (str) is not And(int, <lambda>) (And)",
        ],
    ],
)
def test_error_messages_operator_and(and_data, current_data, error_message):
    assert And(*and_data).validate(current_data) == error_message
