
import pytest

from checker import Checker, And, Or, OptionalKey, SUPPORT_ITER_OBJECTS
from checker_exceptions import (
    CheckerError,
    TypeCheckerError,
    ListCheckerError,
    DictCheckerError
)


CHECKER_DATA_POSITIVE = [
    [int, 1],
    [1, 1],
    ['test', 'test'],
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
    [{'key1': 123}, {'key1': 123}],
    [{'key1': int, 'key2': str, 'key3': bool},
     {'key1': 666, 'key2': '123', 'key3': True}],
    [{'key1': {'key2': str}}, {'key1': {'key2': '123'}}],
    [{'key1': {'key2': {'key3': bool}}}, {'key1': {'key2': {'key3': False}}}],
    [{OptionalKey('key1'): int, 'key2': str}, {'key2': '123'}],
    [{OptionalKey('key1'): int, 'key2': str}, {'key1': 123, 'key2': '123'}],
    [{'key1': Or(int, None)}, {'key1': 123}],
    [{'key1': Or(int, None)}, {'key1': None}],
    [{'key1': And(int, lambda x: 0 < x < 99)}, {'key1': 30}],
    [{'key1': And(list, lambda x: len(x) < 99)}, {'key1': list(range(98))}],
    [{'key1': And(list, lambda x: len(x) < 99)}, {'key1': list([])}],
    [{'key1': And(int, bool)}, {'key1': True}],
    [{'key1': And(str, lambda x: x in ('t', 'e', 's', 't'))}, {'key1': 's'}],
]
CHECKER_DATA_NEGATIVE = [
    [int, '5'],
    [bool, 1],
    [str, True],
    [dict, 12],
    [list, {'key': 1}],
    [tuple, True],
    [frozenset, 'test'],
    [set, []],
    [[int], ['test']],
    [[bool], [1, 2, 3]],
    [[str], list(range(1000))],
    [[int], ['1'] * 1000],
    [[bool], [1, False]],
    [{'key1': int}, {'key1': '1'}],
    [{'key1': int, 'key2': str, 'key3': bool},
     {'key1': 666, 'key2': 123, 'key3': True}],
    [{'key1': {'key2': str}}, {'key1': {'key2': 123}}],
    [{'key1': {'key2': {'key3': bool}}}, {'key1': {'key2': {'key3': 1}}}],
    [{OptionalKey('key1'): int, 'key2': str}, {'key2': 123}],
    [{OptionalKey('key1'): int, 'key2': str}, {'key1': '123', 'key2': 123}],
    [{'key1': Or(int, None)}, {'key1': '123'}],
    [{'key1': Or(int, None)}, {'key1': 'True'}],
    [{'key1': And(int, lambda x: 0 < x < 99)}, {'key1': 99}],
    [{'key1': And(int, lambda x: 0 < x < 99)}, {'key1': 0}],
    [{'key1': And(list, lambda x: len(x) < 99)}, {'key1': list(range(99))}],
    [{'key1': And(int, bool)}, {'key1': None}],
    [{'key1': And(str, lambda x: x in ('t', 'e', 's', 't'))}, {'key1': '1'}],
]
CHECKER_DATA_ASSERT = [
    [[int], []],
    [[int], 122],
    [{'test': bool}, {}],
    [{'test': bool}, []],
    [{'test': bool}, 'test'],
    [{}, {'test': 'test'}],
    [{'test': {'test': bool}}, {'test': {}}],
    [{'test': {'test': bool}}, {'test': 'test'}],
]


def _get_expected_exception(ex_object, soft=False):
    if isinstance(ex_object, SUPPORT_ITER_OBJECTS) and not soft:
        return ListCheckerError
    elif isinstance(ex_object, dict) and not soft:
        return DictCheckerError
    elif issubclass(type(ex_object), type) and not soft:
        return TypeCheckerError
    else:
        return CheckerError


@pytest.mark.parametrize('soft', [True, False])
@pytest.mark.parametrize(('expected', 'current'), CHECKER_DATA_POSITIVE)
def test_checker_positive(expected, current, soft):
    assert Checker(expected, soft).validate(current) == current


@pytest.mark.parametrize('soft', [True, False])
@pytest.mark.parametrize(('expected', 'current'), CHECKER_DATA_NEGATIVE)
def test_checker_negative(expected, current, soft):
    with pytest.raises(_get_expected_exception(expected, soft)):
        Checker(expected, soft).validate(current)


@pytest.mark.parametrize('soft', [True, False])
@pytest.mark.parametrize(('expected', 'current'), CHECKER_DATA_ASSERT)
def test_checker_assert(expected, current, soft):
    with pytest.raises(AssertionError):
        Checker(expected, soft).validate(current)
