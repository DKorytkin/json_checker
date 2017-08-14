
import pytest

from checker import Checker, And, Or, OptionalKey


OR_DATA = [
    [(int, None), 1, None],
    [(int, None), None, None],
    [(int, None), '1', 'Not valid data Or(\'int\', None)\n\tcurrent value "1" is not int\n\tcurrent value "1" is not None']
]
AND_DATA = [
    [(int, lambda x: x > 0), 1, None],
    [(int, bool), True, None],
    [(int, bool), 0, "Not valid data And('int', 'bool')\n\tcurrent value 0 is not bool"],
    [(int, lambda x: x > 0), 0, "Not valid data And('int', '<lambda>')\n\tFunction error <lambda>"],
    [(int, lambda x: x > 0), '1', 'Not valid data And(\'int\', \'<lambda>\')\n\tcurrent value "1" is not int\n\tFunction error <lambda> unorderable types: str() > int()']
]
OPTIONAL_DATA = [
    [{OptionalKey('key'): 'value'}, {'key': 'value'}, {'key': 'value'}],
    [{OptionalKey('key'): 'value', 'key2': 'value2'}, {'key2': 'value2'}, {'key2': 'value2'}]
]
OPERATOR_CLASS_DATA = [
    [Or, 1, 'Or((1,))'],
    [And, 1, 'And((1,))'],
    [OptionalKey, 'test', 'OptionalKey(test)'],
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


@pytest.mark.parametrize('data', OPERATOR_CLASS_DATA)
def test_repr_operator_class(data):
    data_class, test_data, expected_result = data
    c = data_class(test_data)
    assert c.__str__() == expected_result
