
import pytest

from checker import Checker, And, Or, OptionalKey
from checker_exceptions import (
    CheckerError,
    TypeCheckerError,
    ListCheckerError,
    DictCheckerError
)


CHECKER_DATA_POSITIVE = [
    [int, 1],
    [int, True],
    [str, 'test value'],
    [object, 1],
    [bool, True],
    [dict, {'key': 1}],
    [list, [1, ]],
    [tuple, (1, 2)],
    [frozenset, frozenset('2')],
    [set, set('1')],
    [[int], [1]],
    [[int], [1, 2, 3]],
    [[int], list(range(1000))],
    [[str], ['1'] * 1000],
    [[bool], [True, False]],
    [{'key1': int}, {'key1': 123}],
    [{'key1': int, 'key2': str, 'key3': bool},
     {'key1': 666, 'key2': '123', 'key3': True}],
    [{'key1': {'key2': str}}, {'key1': {'key2': '123'}}],
    [{'key1': {'key2': {'key3': bool}}}, {'key1': {'key2': {'key3': False}}}],
    [{OptionalKey('key1'): int, 'key2': str}, {'key2': '123'}],
    [{OptionalKey('key1'): int, 'key2': str}, {'key1': 123, 'key2': '123'}],
    # [{'key1': Or(int, None)}, {'key1': 123}],
    [{'key1': Or(int, None)}, {'key1': None}],
]
CHECKER_DATA_NEGATIVE = [
    [],
]


@pytest.mark.parametrize('soft', [True, False])
@pytest.mark.parametrize(('expected', 'current'), CHECKER_DATA_POSITIVE)
def test_checker_positive(expected, current, soft):
    assert Checker(expected, soft).validate(current) == current


@pytest.mark.skip()
@pytest.mark.parametrize('data', CHECKER_DATA_NEGATIVE)
def test_checker_negative(data):
    expected_data, soft, current_data, exception = data
    with pytest.raises(exception):
        Checker(expected_data, soft).validate(current_data)
