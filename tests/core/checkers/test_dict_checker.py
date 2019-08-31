import pytest

from json_checker.core.checkers import DictChecker
from json_checker.core.exceptions import DictCheckerError, MissKeyCheckerError
from json_checker.core.reports import Report


def test_dict_checker_instance_with_default_param():
    schema = [int]
    soft_report = Report(soft=True)
    c = DictChecker(schema, report=soft_report)
    assert c.expected_data == schema
    assert c.report == soft_report
    assert c.ignore_extra_keys is False
    assert c.soft is True
    assert c.exception == DictCheckerError


def test_dict_checker_instance_with_custom_param():
    schema = [int]
    soft_report = Report(soft=False)
    c = DictChecker(schema, report=soft_report, ignore_extra_keys=True)
    assert c.expected_data == schema
    assert c.report == soft_report
    assert c.ignore_extra_keys is True
    assert c.soft is False
    assert c.exception == DictCheckerError


def test_dict_checker_as_string():
    c = DictChecker(int, report=Report(soft=False))
    assert str(c) == "<DictChecker soft=False expected=int>"


@pytest.mark.parametrize(
    "schema, soft, current_data, expected_result",
    [
        [{"test": int}, True, {"test": 666}, ""],
        [{"test": 666}, True, {"test": 666}, ""],
        [{"test": 666}, False, {"test": 666}, ""],
        [{"test": int}, False, {"test": 666}, ""],
        [{"test": [int]}, True, {"test": [1, 2, 3]}, ""],
        [{"test": [int]}, False, {"test": [1, 2, 3]}, ""],
        [{"test": {"test2": int}}, True, {"test": {"test2": 2}}, ""],
        [{"test": int}, True, {"test": True}, ""],
        [{"test": bool}, True, {"test": False}, ""],
    ],
)
def test_dict_checker_positive(schema, soft, current_data, expected_result):
    dict_checker = DictChecker(
        schema, report=Report(soft), ignore_extra_keys=False
    )
    assert dict_checker.validate(current_data) == expected_result


@pytest.mark.parametrize(
    "schema, current_data, exp_msg",
    [
        [
            {"test": int},
            {"test": "666"},
            "From key=\"test\": \n\tcurrent value '666' (str) is not int",
        ],
        [
            {"test": {"test": 1}},
            {"test": {"test": "666"}},
            'From key="test": \n\t'
            "From key=\"test\": \n\tcurrent value '666' (str) is not 1 (int)",
        ],
    ],
)
def test_dict_checker_positive_message(schema, current_data, exp_msg):
    soft = True
    dict_checker = DictChecker(
        schema, report=Report(soft), ignore_extra_keys=False
    )
    assert dict_checker.validate(current_data) == exp_msg


@pytest.mark.parametrize(
    "dict_data, current_data",
    [
        [{"test": int}, {"test": "666"}],
        [{"test": int}, {"test": {"test1": 1}}],
        [{"test": int}, {"test": {"test1": {"test2": 2}}}],
        [{"test": str}, {"test": 666}],
        [{"test": str}, {"test": []}],
        [{"test": str}, {"test": [1, 2, 3]}],
        [{"test": bool}, {"test": 666}],
    ],
)
def test_dict_checker_negative(dict_data, current_data):
    soft = False
    checker = DictChecker(
        dict_data, report=Report(soft), ignore_extra_keys=False
    )
    with pytest.raises(DictCheckerError):
        checker.validate(current_data)


@pytest.mark.parametrize(
    "dict_data, current_data",
    (
        ({"test": bool}, []),
        ({"test": bool}, "test"),
        ({"test": {"test": bool}}, {"test": "test"}),
    ),
)
def test_dict_checker_assert(dict_data, current_data):
    soft = False
    checker = DictChecker(
        dict_data, report=Report(soft), ignore_extra_keys=False
    )
    with pytest.raises(DictCheckerError):
        checker.validate(current_data)


@pytest.mark.parametrize(
    "ex_data, cu_data, ex_exception",
    (
        ({"test": bool}, {}, MissKeyCheckerError),
        ({"test": {"test": bool}}, {"test": {}}, DictCheckerError),
        ({}, {"test": "test"}, MissKeyCheckerError),
    ),
)
def test_validator_miss_key(ex_data, cu_data, ex_exception):
    soft = False
    checker = DictChecker(
        ex_data, report=Report(soft), ignore_extra_keys=False
    )
    with pytest.raises(ex_exception):
        checker.validate(cu_data)
