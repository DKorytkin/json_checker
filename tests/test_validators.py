
import pytest

from json_checker import (
    And,
    Or,
    OptionalKey,
    TypeCheckerError,
    ListCheckerError,
    DictCheckerError,
    MissKeyCheckerError
)
from json_checker.app import (
    ListChecker,
    TypeChecker,
    DictChecker,
    Validator,
)


TYPE_DATA_POSITIVE = [
    [int, True, 123, None],
    [int, False, 123, None],
    [int, False, True, None],
    [bool, False, True, None],
    [str, False, "1", None],
    [int, True, '123', "current value str is not int"],
    [bool, True, 1, "current value int is not bool"],
    [str, True, [1], "current value list is not str"],
]
TYPE_DATA_NEGATIVE = [
    [str, ["1"]],
    [type, 123],
    [str, [1]],
    [bool, 1],
    [int, '123'],
    [int, []],
]
LIST_DATA_POSITIVE = [
    [[int], False, [1, 2, 3]],
    [[int], True, [1, 2, 3]],
    [[int], False, [True]]
]
LIST_DATA_POSITIVE_MESSAGE = [
    [[int], [1, '2', '3']],
    [[int], [1, 2, None]],
]
LIST_DATA_NEGATIVE = [
    [[int], [1, '2', '3']],
    [[int], [1, 2, None]],
    [[bool], [1, 2]],
    [[int], []],
    [[str], [1, '2', '3']],

]
DICT_DATA_POSITIVE = [
    [{'test': int}, True, {'test': 666}, None],
    [{'test': int}, False, {'test': 666}, None],
    [{'test': [int]}, True, {'test': [1, 2, 3]}, None],
    [{'test': [int]}, False, {'test': [1, 2, 3]}, None],
    [{'test': {'test2': int}}, True, {'test': {'test2': 2}}, None],
    [{'test': int}, True, {'test': True}, None],
    [{'test': bool}, True, {'test': False}, None],
]
DICT_DATA_POSITIVE_MESSAGE = [
    [{'test': int}, {'test': '666'}],
    [{'test': {'test': 1}}, {'test': {'test': '666'}}]
]
DICT_DATA_NEGATIVE = [
    [{'test': int}, {'test': '666'}],
    [{'test': int}, {'test': {'test1': 1}}],
    [{'test': int}, {'test': {'test1': {'test2': 2}}}],
    [{'test': str}, {'test': 666}],
    [{'test': str}, {'test': []}],
    [{'test': str}, {'test': [1, 2, 3, ]}],
    [{'test': bool}, {'test': 666}],
]
DICT_DATA_ASSERT = [
    [{'test': bool}, []],
    [{'test': bool}, 'test'],
    [{'test': {'test': bool}}, {'test': 'test'}],
]
VALIDATOR_DATA_POSITIVE = [
    [lambda x: x > 1, True, 12, None],
    [lambda x: x > 1, False, 12, None],
    [lambda x: x > 1, True, -12, 'Function error <lambda>'],
    [And(int, lambda x: x > 1), False, 12, None],
    [And(str, lambda x: x in ('1', '2')), False, '2', None],
    [And(int, bool), False, True, None],
    [Or(int, None), False, 12, None],
    [Or(int, None), False, None, None],
    [Or(str, lambda x: isinstance(type(x), type)), False, 12, None],
    [{OptionalKey('key'): 'value'}, False, {'key': 'value'}, None],
    [None, True, None, None],
    [None, True, 12, 'current value int is not NoneType'],
    [{'test': And(int, lambda x: x > 1)}, True, {'test': 666}, None],
    [{'test': Or(int, None)}, True, {'test': None}, None],
    [{'test': int}, True, {'test': 666}, None],
    [{'test': int}, False, {'test': 666}, None],
    [{'test': [int]}, False, {'test': [1, 2, 3]}, None],
    [{'test': {'test2': int}}, True, {'test': {'test2': 2}}, None],
    [[int], False, [1, 2, 3], None],
    [[str], True, ['1', '2', '3'], None],
    [[int], False, [True], None],
    [[bool], False, [True, False, True], None],
    [[object], False, [12, False, True, 'test'], None],
    [[{'test1': int, 'test2': str, 'test3': bool}],
     False, [{'test1': 666, 'test2': '22', 'test3': False}], None],
    [int, True, 123, None],
    [123, True, 123, None],
    ['test', True, 'test', None],
    [int, True, '123', 'current value str is not int'],
    [int, False, 123, None],
    [int, False, True, None],
    [bool, False, True, None],
    [str, False, "1", None],
    [str, True, 1, "current value int is not str"],
    ['test', False, "test", None],
    [1, False, 1, None],
]
VALIDATOR_DATA_POSITIVE_MESSAGE = [
    [And(int, lambda x: x > 1), -12, 'Not valid data And'],
    [Or(int, None), '12', 'Not valid data Or'],
    [{OptionalKey('key'): 'value'}, {'key2': 'value2'}, 'Missing keys: key2'],
    [{'test': And(int, lambda x: x > 1)}, {'test': -666}, 'From key="test"'],
    [{'test': Or(int, None)}, {'test': 'None'}, 'From key="test"'],
    [{'test': int}, {'test': '666'}, 'From key="test"'],
    [{'test': [str]}, {'test': ['1', 2, '3']}, 'From key="test"'],
    [[str], [1, '2', 3], 'current value int is not str'],
]
VALIDATOR_DATA_ASSERT = [
    [[int], False, [], []],
]
VALIDATOR_DATA_MISS_KEY = [
    [{'test': bool}, {}],
    [{'test': {'test': bool}}, {'test': {}}],
    [{}, {'test': 'test'}],
]


@pytest.mark.parametrize('data', TYPE_DATA_POSITIVE)
def test_type_checker_positive(data):
    type_data, soft, current_data, expected_result = data
    type_checker = TypeChecker(type_data, soft=soft)
    assert type_checker.validate(current_data) == expected_result


@pytest.mark.parametrize(('type_data', 'current_data'), TYPE_DATA_NEGATIVE)
def test_type_checker_negative(type_data, current_data):
    with pytest.raises(TypeCheckerError):
        TypeChecker(type_data, soft=False).validate(current_data)


@pytest.mark.parametrize('data', LIST_DATA_POSITIVE)
def test_list_checker_positive(data):
    list_data, soft, current_data = data
    list_checker = ListChecker(list_data, soft=soft)
    assert list_checker.validate(current_data) is None


@pytest.mark.parametrize('data', LIST_DATA_POSITIVE_MESSAGE)
def test_list_checker_positive_message(data):
    list_data, current_data = data
    list_checker = ListChecker(list_data, soft=True)
    assert 'current value ' in list_checker.validate(current_data)


@pytest.mark.parametrize(('list_data', 'current_data'), LIST_DATA_NEGATIVE)
def test_list_checker_negative(list_data, current_data):
    with pytest.raises(ListCheckerError):
        ListChecker(list_data, soft=False).validate(current_data)


@pytest.mark.parametrize('data', DICT_DATA_POSITIVE)
def test_dict_checker_positive(data):
    dict_data, soft, current_data, expected_result = data
    dict_checker = DictChecker(dict_data, soft=soft, ignore_extra_keys=False)
    assert dict_checker.validate(current_data) == expected_result


@pytest.mark.parametrize('data', DICT_DATA_POSITIVE_MESSAGE)
def test_dict_checker_positive_message(data):
    dict_data, current_data = data
    dict_checker = DictChecker(dict_data, soft=True, ignore_extra_keys=False)
    assert 'From key="test"' in dict_checker.validate(current_data)


@pytest.mark.parametrize(('dict_data', 'current_data'), DICT_DATA_NEGATIVE)
def test_dict_checker_negative(dict_data, current_data):
    checker = DictChecker(dict_data, soft=False, ignore_extra_keys=False)
    with pytest.raises(DictCheckerError):
        checker.validate(current_data)


@pytest.mark.parametrize(('dict_data', 'current_data'), DICT_DATA_ASSERT)
def test_dict_checker_assert(dict_data, current_data):
    checker = DictChecker(dict_data, soft=False, ignore_extra_keys=False)
    with pytest.raises(AssertionError):
        checker.validate(current_data)


@pytest.mark.parametrize('data', VALIDATOR_DATA_POSITIVE)
def test_validator_positive(data):
    validator_data, soft, current_data, expected_result = data
    validator = Validator(validator_data, soft=soft, ignore_extra_keys=False)
    assert validator.validate(current_data) == expected_result


def test_validator_some_dicts():
    result = Validator(
        data=Or({'key1': int}, {'key2': str}),
        soft=False,
        ignore_extra_keys=False
    ).validate({'key2': 12})
    assert 'Not valid data Or' in result
    assert 'From key="key2": current value int is not str' in result


@pytest.mark.parametrize('data', VALIDATOR_DATA_POSITIVE_MESSAGE)
def test_validator_positive_message(data):
    validator_data, current_data, expected_result = data
    validator = Validator(validator_data, soft=True, ignore_extra_keys=False)
    assert expected_result in validator.validate(current_data)


@pytest.mark.parametrize(('ex_data', 'cu_data'), VALIDATOR_DATA_MISS_KEY)
def test_validator_miss_key(ex_data, cu_data):
    checker = DictChecker(ex_data, soft=False, ignore_extra_keys=False)
    with pytest.raises(MissKeyCheckerError):
        checker.validate(cu_data)
