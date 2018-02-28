
import pytest

from json_checker import Checker, And, Or, OptionalKey
from json_checker.exceptions import (
    CheckerError,
    TypeCheckerError,
    ListCheckerError,
    DictCheckerError,
    MissKeyCheckerError
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
    [[], []],
    [[int], [1, 2, 3]],
    [[int, str, bool], [1, '2', False]],
    [[int, str, bool, [str, bool]], [1, '2', False, ['test', True]]],
    [[int], list(range(1000))],
    [[int], [int]],
    [[1, 2, 3], [1, 2, 3]],
    [[str], ['1'] * 1000],
    [[bool], [True, False]],
    [[{'key1': int}], [{'key1': 1}, {'key1': 1}, {'key1': 1}]],
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
    [{'key1': Or(dict, None)}, {'key1': None}],
    [{'key1': Or(dict, None)}, {'key1': {}}],
    [{'key1': Or(dict, None)}, {'key1': dict}],
    [{'key1': Or(dict, None)}, {'key1': {'key2': 2}}],
    [{'key1': And(int, lambda x: 0 < x < 99)}, {'key1': 30}],
    [{'key1': And(list, lambda x: len(x) < 99)}, {'key1': list(range(98))}],
    [{'key1': And(list, lambda x: len(x) < 99)}, {'key1': list([])}],
    [{'key1': And(int, bool)}, {'key1': True}],
    [{'key1': And(str, lambda x: x in ('t', 'e', 's', 't'))}, {'key1': 's'}],
]
CHECKER_DATA_NEGATIVE = [
    [int, '5'],
    [1, '1'],
    ['test', True],
    [bool, 1],
    [str, True],
    [dict, 12],
    [list, {'key': 1}],
    [tuple, True],
    [frozenset, 'test'],
    [set, []],
    [[int], ['test']],
    [[int], []],
    [[int, str], []],
    [[int], 122],
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
    [{'test': bool}, []],
    [{'test': bool}, 'test'],
    [{'test': {'test': bool}}, {'test': 'test'}],
]
CHECKER_DATA_MISS_KEY = [
    [{'test': bool}, {}],
    [{'key1': bool, 'key2': int}, {}],
    [{}, {'test': 'test'}],
    [{'test': {'test': bool}}, {'test': {}}],
    [{'k1': int}, {'k1': 12, 'k2': 'test'}]
]
CHECKER_CLASS_DATA = [
    [Checker, 1, '1'],
    [Checker, 'test', 'test'],
    [Checker, [1, 2, 3], '[1, 2, 3]'],
    [Checker, {'key': 1}, "{'key': 1}"],
    [Checker, lambda x: x == 1, '<lambda>']
]


def _get_expected_exception(ex_object, soft=False):
    if isinstance(ex_object, (list, tuple, set, frozenset)) and not soft:
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


def test_checker_list_dicts_hard():
    with pytest.raises(DictCheckerError):
        c = Checker([{'key1': int}])
        c.validate([{'key1': 1}, {'key1': 1}, {'key1': '1'}])


def test_checker_list_dicts_soft():
    with pytest.raises(CheckerError):
        c = Checker([{'key1': int}], soft=True)
        c.validate([{'key1': 1}, {'key1': 1}, {'key1': '1'}])


@pytest.mark.parametrize('soft', [True, False])
@pytest.mark.parametrize(('expected', 'current'), CHECKER_DATA_ASSERT)
def test_checker_assert(expected, current, soft):
    with pytest.raises(AssertionError):
        Checker(expected, soft).validate(current)


@pytest.mark.parametrize('data', CHECKER_CLASS_DATA)
def test_repr_checker_class(data):
    data_class, test_data, expected_result = data
    c = data_class(test_data, soft=True)
    assert c.__str__() == expected_result


@pytest.mark.parametrize(('expected', 'current'), CHECKER_DATA_MISS_KEY)
def test_miss_keys(expected, current):
    with pytest.raises(MissKeyCheckerError):
        Checker(expected).validate(current)


@pytest.mark.parametrize(('expected', 'current'), CHECKER_DATA_MISS_KEY)
def test_miss_keys_soft(expected, current):
    with pytest.raises(CheckerError):
        Checker(expected, soft=True).validate(current)
