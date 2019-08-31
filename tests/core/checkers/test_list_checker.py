import pytest

from json_checker.core.checkers import ListChecker
from json_checker.core.exceptions import ListCheckerError
from json_checker.core.reports import Report


def test_list_checker_instance_with_default_param():
    schema = [int]
    soft_report = Report(soft=True)
    c = ListChecker(schema, report=soft_report)
    assert c.expected_data == schema
    assert c.report == soft_report
    assert c.ignore_extra_keys is False
    assert c.soft is True
    assert c.exception == ListCheckerError


def test_list_checker_instance_with_custom_param():
    schema = [int]
    soft_report = Report(soft=False)
    c = ListChecker(schema, report=soft_report, ignore_extra_keys=True)
    assert c.expected_data == schema
    assert c.report == soft_report
    assert c.ignore_extra_keys is True
    assert c.soft is False
    assert c.exception == ListCheckerError


def test_list_checker_as_string():
    c = ListChecker([int], report=Report(soft=False))
    assert str(c) == "<ListChecker soft=False expected=[<class 'int'>] (list)>"


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
                "current value '3' (str) is not int",
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
        [[int], [1, "2", "3"], ListCheckerError],
        [[int], [1, 2, None], ListCheckerError],
        [[bool], [1, 2], ListCheckerError],
        [["1", "2"], [1, 2], ListCheckerError],
        [[str, int], [1, "2"], ListCheckerError],
        [[int], [], ListCheckerError],
        [[int], None, ListCheckerError],
        [[], [1, 2, 3], ListCheckerError],
        [[str], [1, "2", "3"], ListCheckerError],
    ],
)
def test_list_checker_negative(list_data, current_data, ex_exception):
    soft = False
    list_checker = ListChecker(
        expected_data=list_data, report=Report(soft=soft)
    )
    with pytest.raises(ex_exception):
        list_checker.validate(current_data)
