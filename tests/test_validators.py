
import pytest

from checker import ListChecker
from checker_exceptions import TypeCheckerError


SOFT_ERROR_STR = (
    "ListCheckerErrors:\n\tTypeCheckerError: current type <class 'str'>, "
    "expected type <class 'int'>, current value \"2\"\n\t"
    "TypeCheckerError: current type <class 'str'>, expected type "
    "<class 'int'>, current value \"3\""
)
HARD_ERROR_STR = (
    "\ncurrent type <class 'str'>, "
    "expected type <class 'int'>, current value \"2\""
)
SOFT_NONE_ERROR_STR = (
    "ListCheckerErrors:\n\tTypeCheckerError: "
    "current type <class 'NoneType'>, expected type "
    "<class 'int'>, current value null"
)
HARD_NONE_ERROR_STR = (
    "\ncurrent type <class 'NoneType'>, "
    "expected type <class 'int'>, current value null"
)


LIST_DATA = [
    [[int], False, [1, 2, 3], None],
    [[int], True, [1, 2, 3], None],
    [[int], True, [1, '2', '3'], SOFT_ERROR_STR],
    [[int], False, [1, '2', '3'], HARD_ERROR_STR],
    [[int], True, [1, 2, None], SOFT_NONE_ERROR_STR],
    [[int], False, [1, 2, None], HARD_NONE_ERROR_STR],
    [[int], False, [], None],
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
