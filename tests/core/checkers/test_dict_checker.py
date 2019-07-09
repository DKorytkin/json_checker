import pytest

from json_checker.core.checkers import DictChecker
from json_checker.core.exceptions import DictCheckerError, MissKeyCheckerError
from json_checker.core.reports import Report


@pytest.mark.parametrize('dict_data, soft, current_data, expected_result', [
    [{'test': int}, True, {'test': 666}, None],
    [{'test': 666}, True, {'test': 666}, None],
    [{'test': 666}, False, {'test': 666}, None],
    [{'test': int}, False, {'test': 666}, None],
    [{'test': [int]}, True, {'test': [1, 2, 3]}, None],
    [{'test': [int]}, False, {'test': [1, 2, 3]}, None],
    [{'test': {'test2': int}}, True, {'test': {'test2': 2}}, None],
    [{'test': int}, True, {'test': True}, None],
    [{'test': bool}, True, {'test': False}, None]])
def test_dict_checker_positive(dict_data, soft, current_data, expected_result):
    dict_checker = DictChecker(dict_data, soft=soft, report=Report(soft), ignore_extra_keys=False)
    assert dict_checker.validate(current_data) == expected_result


@pytest.mark.parametrize('dict_data, current_data', [
    [{'test': int}, {'test': '666'}],
    [{'test': {'test': 1}}, {'test': {'test': '666'}}]])
def test_dict_checker_positive_message(dict_data, current_data):
    soft = True
    dict_checker = DictChecker(dict_data, soft=soft, report=Report(soft), ignore_extra_keys=False)
    assert 'From key="test"' in dict_checker.validate(current_data)


@pytest.mark.parametrize('dict_data, current_data', [
    [{'test': int}, {'test': '666'}],
    [{'test': int}, {'test': {'test1': 1}}],
    [{'test': int}, {'test': {'test1': {'test2': 2}}}],
    [{'test': str}, {'test': 666}],
    [{'test': str}, {'test': []}],
    [{'test': str}, {'test': [1, 2, 3, ]}],
    [{'test': bool}, {'test': 666}]])
def test_dict_checker_negative(dict_data, current_data):
    soft = False
    checker = DictChecker(dict_data, soft=soft, report=Report(soft), ignore_extra_keys=False)
    with pytest.raises(DictCheckerError):
        checker.validate(current_data)


@pytest.mark.parametrize('dict_data, current_data', (
    ({'test': bool}, []),
    ({'test': bool}, 'test'),
    ({'test': {'test': bool}}, {'test': 'test'})))
def test_dict_checker_assert(dict_data, current_data):
    soft = False
    checker = DictChecker(dict_data, soft=soft, report=Report(soft), ignore_extra_keys=False)
    with pytest.raises(DictCheckerError):
        checker.validate(current_data)


@pytest.mark.parametrize('ex_data, cu_data, ex_exception', (
    ({'test': bool}, {}, MissKeyCheckerError),
    ({'test': {'test': bool}}, {'test': {}}, DictCheckerError),
    ({}, {'test': 'test'}, MissKeyCheckerError)))
def test_validator_miss_key(ex_data, cu_data, ex_exception):
    soft = False
    checker = DictChecker(ex_data, soft=soft, report=Report(soft), ignore_extra_keys=False)
    with pytest.raises(ex_exception):
        checker.validate(cu_data)
