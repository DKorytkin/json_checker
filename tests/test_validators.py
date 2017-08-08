
import pytest

from checker import ListChecker, TypeChecker
from checker_exceptions import TypeCheckerError


LIST_DATA = [
    [[int], False, [1, 2, 3], None],
    [[int], True, [1, 2, 3], None],
    [[int], True, [1, '2', '3'], "ListCheckerErrors:\n\tTypeCheckerError: current type <class 'str'>, expected type <class 'int'>, current value \"2\"\n\tTypeCheckerError: current type <class 'str'>, expected type <class 'int'>, current value \"3\""],
    [[int], False, [1, '2', '3'], "\ncurrent type <class 'str'>, expected type <class 'int'>, current value \"2\""],
    [[int], True, [1, 2, None], "ListCheckerErrors:\n\tTypeCheckerError: current type <class 'NoneType'>, expected type <class 'int'>, current value null"],
    [[int], False, [1, 2, None], "\ncurrent type <class 'NoneType'>, expected type <class 'int'>, current value null"],
    [[int], False, [], None],
]
TYPE_DATA = [
    [int, True, 123, None],
    [int, False, 123, None],
    [int, False, True, None],
    [int, False, '123', "\ncurrent type <class 'str'>, expected type <class 'int'>, current value \"123\""],
    [int, True, '123', "TypeCheckerError: current type <class 'str'>, expected type <class 'int'>, current value \"123\""],
    [int, False, [], "\ncurrent type <class 'list'>, expected type <class 'int'>, current value []"],
    [bool, False, True, None],
    [bool, False, 1, "\ncurrent type <class 'int'>, expected type <class 'bool'>, current value 1"],
    [bool, True, 1, "TypeCheckerError: current type <class 'int'>, expected type <class 'bool'>, current value 1"],
    [str, False, [1], "\ncurrent type <class 'list'>, expected type <class 'str'>, current value [1]"],
    [str, True, [1], "TypeCheckerError: current type <class 'list'>, expected type <class 'str'>, current value [1]"],
    [str, False, "1", None],
    [str, False, ["1"], "\ncurrent type <class 'list'>, expected type <class 'str'>, current value [\"1\"]"],
]


@pytest.mark.parametrize('data', LIST_DATA)
def test_list_checker(data):
    list_data, soft, current_data, expected_result = data
    list_checker = ListChecker(list_data, soft=soft)
    try:
        result = list_checker.validate(current_data)
    except TypeCheckerError as e:
        result = e.__str__()
    assert result == expected_result


@pytest.mark.parametrize('data', TYPE_DATA)
def test_type_checker(data):
    type_data, soft, current_data, expected_result = data
    type_checker = TypeChecker(type_data, soft=soft)
    try:
        result = type_checker.validate(current_data)
    except TypeCheckerError as e:
        result = e.__str__()
    assert result == expected_result
