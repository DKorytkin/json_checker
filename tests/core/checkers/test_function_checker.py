import pytest

from json_checker.core.checkers import FunctionChecker
from json_checker.core.exceptions import FunctionCheckerError
from json_checker.core.reports import Report


def foo(x):
    return 99 > x > 1


def test_function_checker_instance_with_default_params():
    soft_report = Report(soft=True)
    c = FunctionChecker(foo, report=soft_report)
    assert c.expected_data == foo
    assert c.report == soft_report
    assert c.ignore_extra_keys is False
    assert c.soft is True
    assert c.exception == FunctionCheckerError


def test_function_checker_instance_with_custom_params():
    soft_report = Report(soft=False)
    c = FunctionChecker(foo, report=soft_report, ignore_extra_keys=True)
    assert c.expected_data == foo
    assert c.report == soft_report
    assert c.ignore_extra_keys is True
    assert c.soft is False
    assert c.exception == FunctionCheckerError


def test_function_checker_as_string():
    c = FunctionChecker(foo, report=Report(soft=True))
    assert str(c) == "<FunctionChecker soft=True expected=foo>"


@pytest.mark.parametrize("data", (98, 55, 2))
def test_soft_function_checker_with_valid_data(data):
    soft_report = Report(soft=True)
    c = FunctionChecker(foo, report=soft_report)
    result = c.validate(data)
    assert result == soft_report
    assert not result.has_errors()


@pytest.mark.parametrize("data", (99, 100, 1, 0, -1))
def test_soft_function_checker_with_not_valid_data(data):
    soft_report = Report(soft=True)
    c = FunctionChecker(foo, report=soft_report)
    result = c.validate(data)
    assert result == soft_report
    assert result.has_errors()
    assert str(result) == "function error: foo with data %s (int)" % data


@pytest.mark.parametrize("data", (None, "", [], {}))
def test_soft_function_checker_with_invalid_data(data):
    exp_message = (
        "function error: foo with data '>' not supported "
        "between instances of 'int' and '%s'" % type(data).__name__
    )
    soft_report = Report(soft=True)
    c = FunctionChecker(foo, report=soft_report)
    result = c.validate(data)
    assert result == soft_report
    assert result.has_errors()
    assert str(result) == exp_message


@pytest.mark.parametrize("data", (98, 55, 2))
def test_hard_function_checker_with_valid_data(data):
    hard_report = Report(soft=False)
    c = FunctionChecker(foo, report=hard_report)
    result = c.validate(data)
    assert result == hard_report
    assert not result.has_errors()


@pytest.mark.parametrize("data", (99, 100, 1, 0, -1, None, "", [], {}))
def test_hard_function_checker_with_not_valid_data(data):
    hard_report = Report(soft=False)
    c = FunctionChecker(foo, report=hard_report)
    with pytest.raises(FunctionCheckerError):
        assert c.validate(data)
