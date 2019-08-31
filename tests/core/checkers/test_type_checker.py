import pytest

from json_checker.core.exceptions import TypeCheckerError
from json_checker.core.checkers import TypeChecker
from json_checker.core.reports import Report


def test_type_checker_instance_with_default_param():
    schema = [int]
    soft_report = Report(soft=True)
    c = TypeChecker(schema, report=soft_report)
    assert c.expected_data == schema
    assert c.report == soft_report
    assert c.ignore_extra_keys is False
    assert c.soft is True
    assert c.exception == TypeCheckerError


def test_type_checker_instance_with_custom_param():
    schema = [int]
    soft_report = Report(soft=False)
    c = TypeChecker(schema, report=soft_report, ignore_extra_keys=True)
    assert c.expected_data == schema
    assert c.report == soft_report
    assert c.ignore_extra_keys is True
    assert c.soft is False
    assert c.exception == TypeCheckerError


def test_type_checker_as_string():
    c = TypeChecker(int, report=Report(soft=False))
    assert str(c) == "<TypeChecker soft=False expected=int>"


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
