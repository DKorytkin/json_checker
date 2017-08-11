
import pytest

from checker import (
    Checker,
    ListChecker,
    TypeChecker,
    DictChecker,
    Validator,
    And,
    Or,
    OptionalKey
)
from checker_exceptions import (
    TypeCheckerError,
    ListCheckerError,
    DictCheckerError
)


TYPE_DATA_POSITIVE = [
    [int, True, 123, None],
    [int, False, 123, None],
    [int, False, True, None],
    # [len, False, [1, 2], None], TODO unskip after fix
    [bool, False, True, None],
    [str, False, "1", None],
    [int, True, '123', "current value \"123\" is not int"],
    [bool, True, 1, "current value 1 is not bool"],
    [str, True, [1], "current value [1] is not str"],
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
    [[int], False, [1, 2, 3], None],
    [[int], True, [1, 2, 3], None],
    [[int], False, [], None],
    [[int], False, [True], None],
    [[int], True, [1, '2', '3'], "ListCheckerErrors:\ncurrent value \"2\" is not int\ncurrent value \"3\" is not int"],
    [[int], True, [1, 2, None], "ListCheckerErrors:\ncurrent value None is not int"],

]
LIST_DATA_NEGATIVE = [
    [[int], [1, '2', '3']],
    [[int], [1, 2, None]],
    [[bool], [1, 2]],
    [[str], [1, '2', '3']],

]
DICT_DATA_POSITIVE = [
    [{'test': int}, True, {'test': 666}, None],
    [{'test': int}, False, {'test': 666}, None],
    [{'test': int}, True, {'test': '666'}, 'DictCheckerErrors:\nFrom key="test"\n\tcurrent value "666" is not int'],
    [{'test': [int]}, True, {'test': [1, 2, 3]}, None],
    [{'test': [int]}, False, {'test': [1, 2, 3]}, None],
    [{'test': {'test2': int}}, True, {'test': {'test2': 2}}, None],
    [{'test': int}, True, {'test': True}, None],
    [{'test': bool}, True, {'test': False}, None],
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
    [{'test': bool}, {}],
    [{'test': bool}, []],
    [{'test': bool}, 'test'],
    [{}, {'test': 'test'}],
    [{'test': {'test': bool}}, {'test': {}}],
    [{'test': {'test': bool}}, {'test': 'test'}],
]
VALIDATOR_DATA_POSITIVE = [
    [lambda x: x > 1, True, 12, []],
    [lambda x: x > 1, False, 12, []],
    [lambda x: x > 1, True, -12, 'Function error <lambda>'],
    [And(int, lambda x: x > 1), False, 12, []],
    [And(str, lambda x: x in ('1', '2')), False, '2', []],
    [And(int, lambda x: x > 1), True, -12, ["Not valid data And('int', '<lambda>')\n\tFunction error <lambda>"]],
    [And(int, bool), False, True, []],
    [Or(int, None), False, 12, []],
    [Or(int, None), False, None, []],
    [Or(int, None), False, '12', ["Not valid data Or('int', None)\n\tcurrent value \"12\" is not int\n\tcurrent value \"12\" is not None"]],
    [Or(str, lambda x: isinstance(type(x), type)), False, 12, []],
    [{OptionalKey('key'): 'value'}, False, {'key': 'value'}, []],
    [{OptionalKey('key'): 'value'}, False, {'key2': 'value2'}, []],
    [None, True, None, []],
    [None, True, 12, 'current value 12 is not None'],
    [{'test': And(int, lambda x: x > 1)}, True, {'test': 666}, []],
    [{'test': And(int, lambda x: x > 1)}, True, {'test': -666}, ["DictCheckerErrors:\nFrom key=\"test\"\n\tNot valid data And('int', '<lambda>')\n\tFunction error <lambda>"]],
    [{'test': Or(int, None)}, True, {'test': 'None'}, ['DictCheckerErrors:\nFrom key="test"\n\tNot valid data Or(\'int\', None)\n\tcurrent value "None" is not int\n\tcurrent value "None" is not None']],
    [{'test': Or(int, None)}, True, {'test': None}, []],
    [{'test': int}, True, {'test': 666}, []],
    [{'test': int}, True, {'test': '666'}, ['DictCheckerErrors:\nFrom key="test"\n\tcurrent value "666" is not int']],
    [{'test': int}, False, {'test': 666}, []],
    [{'test': [int]}, False, {'test': [1, 2, 3]}, []],
    [{'test': [str]}, True, {'test': ['1', 2, '3']}, ["DictCheckerErrors:\nFrom key=\"test\"\n\tListCheckerErrors:\ncurrent value 2 is not str"]],
    [{'test': {'test2': int}}, True, {'test': {'test2': 2}}, []],
    [[int], False, [1, 2, 3], []],
    [[str], True, ['1', '2', '3'], []],
    [[str], True, [1, '2', 3], ["ListCheckerErrors:\ncurrent value 1 is not str\ncurrent value 3 is not str"]],
    [[int], False, [True], []],
    [[bool], False, [True, False, True], []],
    [[object], False, [12, False, True, 'test'], []],
    [[{'test1': int, 'test2': str, 'test3': bool}],
     False, [{'test1': 666, 'test2': '22', 'test3': False}], []],
    [int, True, 123, []],
    [int, True, '123', "current value \"123\" is not int"],
    [int, False, 123, []],
    [int, False, True, []],
    [bool, False, True, []],
    [str, False, "1", []],
    [str, True, 1, "current value 1 is not str"],
    ['test', False, "test", []],
    [1, False, 1, []],
]
VALIDATOR_DATA_ASSERT = [
    [[int], False, [], []],
]
CHECKER_CLASS_DATA = [
    [ListChecker, [1, 2, 3], 'ListChecker([1, 2, 3])'],
    [TypeChecker, 1, 'TypeChecker(1)'],
    [DictChecker, {'t': 1}, "DictChecker({'t': 1})"],
    [Validator, 1, 'Validator(1)'],
    [Checker, 1, '1'],
    [Checker, lambda x: x == 1, '<lambda>']
]
OPERATOR_CLASS_DATA = [
    [Or, 1, 'Or((1,))'],
    [And, 1, 'And((1,))'],
    [OptionalKey, 'test', 'OptionalKey(test)'],
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
    list_data, soft, current_data, expected_result = data
    list_checker = ListChecker(list_data, soft=soft)
    assert list_checker.validate(current_data) == expected_result


@pytest.mark.parametrize(('list_data', 'current_data'), LIST_DATA_NEGATIVE)
def test_list_checker_negative(list_data, current_data):
    with pytest.raises(ListCheckerError):
        ListChecker(list_data, soft=False).validate(current_data)


@pytest.mark.parametrize('data', DICT_DATA_POSITIVE)
def test_dict_checker_positive(data):
    dict_data, soft, current_data, expected_result = data
    dict_checker = DictChecker(dict_data, soft=soft)
    assert dict_checker.validate(current_data) == expected_result


@pytest.mark.parametrize(('dict_data', 'current_data'), DICT_DATA_NEGATIVE)
def test_dict_checker_negative(dict_data, current_data):
    with pytest.raises(DictCheckerError):
        DictChecker(dict_data, soft=False).validate(current_data)


@pytest.mark.parametrize(('dict_data', 'current_data'), DICT_DATA_ASSERT)
def test_dict_checker_assert(dict_data, current_data):
    with pytest.raises(AssertionError):
        DictChecker(dict_data, soft=False).validate(current_data)


@pytest.mark.parametrize('data', VALIDATOR_DATA_POSITIVE)
def test_validator_positive(data):
    validator_data, soft, current_data, expected_result = data
    validator = Validator(validator_data, soft=soft)
    assert validator.validate(current_data) == expected_result


@pytest.mark.parametrize('data', CHECKER_CLASS_DATA)
def test_repr_checker_class(data):
    data_class, test_data, expected_result = data
    c = data_class(test_data, soft=True)
    assert c.__str__() == expected_result


@pytest.mark.parametrize('data', OPERATOR_CLASS_DATA)
def test_repr_operator_class(data):
    data_class, test_data, expected_result = data
    c = data_class(test_data)
    assert c.__str__() == expected_result
