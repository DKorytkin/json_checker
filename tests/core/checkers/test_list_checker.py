import pytest

from json_checker.core.checkers import ListChecker
from json_checker.core.exceptions import ListCheckerError, TypeCheckerError
from json_checker.core.reports import Report


@pytest.mark.parametrize(
    "list_data, soft, current_data",
    (
        ([1, 2], False, [1, 2]),
        ([int, int], False, [1, 2]),
        ([int, str], False, [1, "x"]),
        ([1, 2], True, [1, 2]),
        ([int], False, [1, 2, 3]),
        ([int], True, [1, 2, 3]),
        ([int], False, [True]),
    ),
)
def test_list_checker_positive(list_data, soft, current_data):
    list_checker = ListChecker(
        expected_data=list_data, report=Report(soft=soft)
    )
    assert list_checker.validate(current_data) == ""


@pytest.mark.parametrize(
    "list_data, current_data, ex_message",
    (
        (
            [int],
            [1, "2", "3"],
            [
                "current value '2' (str) is not int",
                "current value '3' (str) is not int"
            ],
        ),
        ([int], [1, 2, None], ["current value None is not int"]),
    ),
)
def test_list_checker_positive_message(list_data, current_data, ex_message):
    soft = True
    list_checker = ListChecker(
        expected_data=list_data, report=Report(soft=soft)
    )
    assert list_checker.validate(current_data) == ex_message


@pytest.mark.parametrize(
    "list_data, current_data, ex_exception",
    [
        [[int], [1, "2", "3"], TypeCheckerError],
        [[int], [1, 2, None], TypeCheckerError],
        [[bool], [1, 2], TypeCheckerError],
        [["1", "2"], [1, 2], TypeCheckerError],
        [[str, int], [1, "2"], TypeCheckerError],
        [[int], [], ListCheckerError],
        [[int], None, ListCheckerError],
        [[], [1, 2, 3], ListCheckerError],
        [[str], [1, "2", "3"], TypeCheckerError],
    ],
)
def test_list_checker_negative(list_data, current_data, ex_exception):
    soft = False
    list_checker = ListChecker(
        expected_data=list_data, report=Report(soft=soft)
    )
    with pytest.raises(ex_exception):
        list_checker.validate(current_data)
