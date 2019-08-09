
import pytest

from json_checker import Checker, And, Or, OptionalKey
from json_checker.core.exceptions import (
    CheckerError,
    TypeCheckerError,
    ListCheckerError,
    DictCheckerError,
    MissKeyCheckerError
)


def test_create_checker_instance_with_default_param():
    c = Checker(int)
    assert c.expected_data is int
    assert c.soft is False
    assert c.ignore_extra_keys is False


def test_create_checker_instance_with_custom_param():
    c = Checker(int, True, True)
    assert c.expected_data is int
    assert c.soft is True
    assert c.ignore_extra_keys is True


def test_checker_string_with_callable_data():
    c = Checker(lambda x: x is True)
    assert str(c) == '<Checker soft=False expected=<lambda>>'


def test_checker_string():
    c = Checker(int)
    assert str(c) == '<Checker soft=False expected=int>'


@pytest.mark.parametrize('test_data, expected_result', [
    [1, '<Checker soft=True expected=1 (int)>'],
    ['test', "<Checker soft=True expected='test' (str)>"],
    [[1, 2, 3], '<Checker soft=True expected=[1, 2, 3] (list)>'],
    [{'key': 1}, "<Checker soft=True expected={'key': 1} (dict)>"],
    [lambda x: x == 1, '<Checker soft=True expected=<lambda>>']])
def test_repr_checker_class(test_data, expected_result):
    c = Checker(test_data, soft=True)
    assert c.__str__() == expected_result


@pytest.mark.parametrize('soft', [True, False])
@pytest.mark.parametrize(('expected', 'current'), [
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
    [{'key1': And(str, lambda x: x in ('t', 'e', 's', 't'))}, {'key1': 's'}]])
def test_checker_positive(expected, current, soft):
    assert Checker(expected, soft).validate(current) == current


@pytest.mark.parametrize(('expected', 'current'), [
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
    [{'key1': And(str, lambda x: x in ('t', 'e', 's', 't'))}, {'key1': '1'}]])
def test_soft_checker_with_errors(expected, current):
    with pytest.raises(CheckerError):
        Checker(expected, soft=True).validate(current)


@pytest.mark.parametrize('expected, current, exception', (
    [int, '5', TypeCheckerError],
    [1, '1', TypeCheckerError],
    ['test', True, TypeCheckerError],
    [bool, 1, TypeCheckerError],
    [str, True, TypeCheckerError],
    [dict, 12, TypeCheckerError],
    [list, {'key': 1}, TypeCheckerError],
    [tuple, True, TypeCheckerError],
    [frozenset, 'test', TypeCheckerError],
    [set, [], TypeCheckerError],
    [[int], ['test'], TypeCheckerError],
    [[int], [], ListCheckerError],
    [[int, str], [], ListCheckerError],
    [[int], 122, ListCheckerError],
    [[bool], [1, 2, 3], TypeCheckerError],
    [[str], list(range(1000)), TypeCheckerError],
    [[int], ['1'] * 1000, TypeCheckerError],
    [[bool], [1, False], TypeCheckerError],
    [{'key1': int}, {'key1': '1'}, DictCheckerError],
    [{'key1': int, 'key2': str, 'key3': bool},
     {'key1': 666, 'key2': 123, 'key3': True}, DictCheckerError],
    [{'key1': {'key2': str}}, {'key1': {'key2': 123}}, DictCheckerError],
    [{'key1': {'key2': {'key3': bool}}}, {'key1': {'key2': {'key3': 1}}}, DictCheckerError],
    [{OptionalKey('key1'): int, 'key2': str}, {'key2': 123}, DictCheckerError],
    [{OptionalKey('key1'): int, 'key2': str}, {'key1': '123', 'key2': 123}, DictCheckerError],
    [{'key1': Or(int, None)}, {'key1': '123'}, DictCheckerError],
    [{'key1': Or(int, None)}, {'key1': 'True'}, DictCheckerError],
    [{'key1': And(int, lambda x: 0 < x < 99)}, {'key1': 99}, DictCheckerError],
    [{'key1': And(int, lambda x: 0 < x < 99)}, {'key1': 0}, DictCheckerError],
    [{'key1': And(list, lambda x: len(x) < 99)}, {'key1': list(range(99))}, DictCheckerError],
    [{'key1': And(int, bool)}, {'key1': None}, DictCheckerError],
    [{'key1': And(str, lambda x: x in ('t', 'e', 's', 't'))}, {'key1': '1'}, DictCheckerError]))
def test_checker_with_errors(expected, current, exception):
    with pytest.raises(exception):
        Checker(expected, soft=False).validate(current)


def test_checker_list_dicts_hard():
    with pytest.raises(DictCheckerError):
        c = Checker([{'key1': int}])
        c.validate([{'key1': 1}, {'key1': 1}, {'key1': '1'}])


def test_checker_list_dicts_soft():
    with pytest.raises(CheckerError):
        c = Checker([{'key1': int}], soft=True)
        c.validate([{'key1': 1}, {'key1': 1}, {'key1': '1'}])


@pytest.mark.parametrize('soft', [True, False])
@pytest.mark.parametrize(('expected', 'current'), [
    [{'test': bool}, []],
    [{'test': bool}, 'test'],
    [{'test': {'test': bool}}, {'test': 'test'}]])
def test_checker_assert(expected, current, soft):
    with pytest.raises(CheckerError):
        Checker(expected, soft).validate(current)


@pytest.mark.parametrize('expected, current, exp_exception', [
    [{'test': bool}, {}, MissKeyCheckerError],
    [{'key1': bool, 'key2': int}, {}, MissKeyCheckerError],
    [{}, {'test': 'test'}, MissKeyCheckerError],
    [{'test': {'test': bool}}, {'test': {}}, DictCheckerError],
    [{'k1': int}, {'k1': 12, 'k2': 'test'}, MissKeyCheckerError]])
def test_miss_keys(expected, current, exp_exception):
    with pytest.raises(exp_exception):
        Checker(expected).validate(current)


@pytest.mark.parametrize('expected, current', [
    [{'test': bool}, {}],
    [{'key1': bool, 'key2': int}, {}],
    [{}, {'test': 'test'}],
    [{'test': {'test': bool}}, {'test': {}}],
    [{'k1': int}, {'k1': 12, 'k2': 'test'}]])
def test_miss_keys_soft(expected, current):
    with pytest.raises(CheckerError):
        Checker(expected, soft=True).validate(current)
