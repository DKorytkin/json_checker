
import pytest

from checker import Checker, And, Or, OptionalKey


OR_DATA = [
    [(int, None), 1, None],
    [(int, None), None, None],
    [(int, None), '1', "\n\t Not valid data Or('int', None)"]
]
AND_DATA = [
    [(int, lambda x: x > 0), 1, None],
    [(int, bool), True, None],
    [(int, bool), 0, "\n\t Not valid data And('int', 'bool')"],
    [(int, lambda x: x > 0), 0, "\n\t Not valid data And('int', '<lambda>')"],
    # [(int, lambda x: x > 0), '1', None] # TODO unskip after fix
]
OPTIONAL_DATA = [
    [{OptionalKey('key'): 'value'}, {'key': 'value'}, {'key': 'value'}],
    [{OptionalKey('key'): 'value'}, {'key2': 'value2'}, {'key2': 'value2'}]
]


@pytest.mark.parametrize('data', OR_DATA)
def test_operator_or(data):
    or_data, current_data, expected_result = data
    assert Or(*or_data).validate(current_data) == expected_result


@pytest.mark.parametrize('data', AND_DATA)
def test_operator_and(data):
    and_data, current_data, expected_result = data
    assert And(*and_data).validate(current_data) == expected_result


@pytest.mark.parametrize('data', OPTIONAL_DATA)
def test_operator_optional_key(data):
    optional_data, current_data, expected_result = data
    assert Checker(optional_data).validate(current_data) == expected_result


def test_operator_optional_key_assert():
    with pytest.raises(AssertionError):
        Checker({OptionalKey('key'): 'value'}).validate({})
