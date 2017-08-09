
import pytest

from checker import ListChecker, TypeChecker, DictChecker
from checker_exceptions import ListCheckerError, DictCheckerError


TYPE_DATA = [
    [int, True, 123, None],
    [int, False, 123, None],
    [int, False, True, None],
    # [len, False, [1, 2], None], TODO unskip after fix
    [bool, False, True, None],
    [str, False, "1", None],
    [int, False, '123', "current type <class 'str'>, expected type <class 'int'>, current value \"123\""],
    [int, True, '123', "current type <class 'str'>, expected type <class 'int'>, current value \"123\""],
    [int, False, [], "current type <class 'list'>, expected type <class 'int'>, current value []"],
    [bool, False, 1, "current type <class 'int'>, expected type <class 'bool'>, current value 1"],
    [bool, True, 1, "current type <class 'int'>, expected type <class 'bool'>, current value 1"],
    [str, False, [1], "current type <class 'list'>, expected type <class 'str'>, current value [1]"],
    [str, True, [1], "current type <class 'list'>, expected type <class 'str'>, current value [1]"],
    [str, False, ["1"], "current type <class 'list'>, expected type <class 'str'>, current value [\"1\"]"],
]
LIST_DATA_POSITIVE = [
    [[int], False, [1, 2, 3], None],
    [[int], True, [1, 2, 3], None],
    [[int], False, [], None],
    [[int], False, [True], None],
    [[int], True, [1, '2', '3'], "ListCheckerErrors:\ncurrent type <class 'str'>, expected type <class 'int'>, current value \"2\"\ncurrent type <class 'str'>, expected type <class 'int'>, current value \"3\""],
    [[int], True, [1, 2, None], "ListCheckerErrors:\ncurrent type <class 'NoneType'>, expected type <class 'int'>, current value null"],

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
    [{'test': int}, True, {'test': '666'}, 'DictCheckerErrors:\nFrom key="test"\n\tcurrent type <class \'str\'>, expected type <class \'int\'>, current value "666"'],
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
    [{'test': {'test': bool}}, {'test': {}}],
]


@pytest.mark.parametrize('data', TYPE_DATA)
def test_type_checker(data):
    type_data, soft, current_data, expected_result = data
    type_checker = TypeChecker(type_data, soft=soft)
    assert type_checker.validate(current_data) == expected_result


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
