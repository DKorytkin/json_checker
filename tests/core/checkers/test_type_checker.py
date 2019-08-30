import pytest

from json_checker.core.exceptions import TypeCheckerError
from json_checker.core.checkers import TypeChecker
from json_checker.core.reports import Report


@pytest.mark.parametrize(
    "type_data, soft, current_data, expected_result",
    [
        [int, True, 123, ""],
        [int, False, 123, ""],
        [int, False, True, ""],
        [bool, False, True, ""],
        [str, False, "1", ""],
        [int, True, "123", "current value '123' (str) is not int"],
        [bool, True, 1, "current value 1 (int) is not bool"],
        [str, True, [1], "current value [1] (list) is not str"],
    ],
)
def test_type_checker_positive(type_data, soft, current_data, expected_result):
    report = Report(soft=soft)
    type_checker = TypeChecker(expected_data=type_data, report=report)
    result = type_checker.validate(current_data)
    assert isinstance(result, Report)
    assert result == report
    assert result == expected_result


@pytest.mark.parametrize(
    "type_data, current_data",
    [
        [str, ["1"]],
        [type, 123],
        [str, [1]],
        [bool, 1],
        [int, "123"],
        [int, []],
    ],
)
def test_type_checker_negative(type_data, current_data):
    r = Report(soft=False)
    type_checker = TypeChecker(expected_data=type_data, report=r)
    with pytest.raises(TypeCheckerError):
        type_checker.validate(current_data)