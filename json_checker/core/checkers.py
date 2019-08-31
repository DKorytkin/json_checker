import logging
from types import FunctionType
from typing import Any, Iterable, Iterator

from collections import OrderedDict

from json_checker.core.base import (
    BaseOperator,
    BaseValidator,
    format_data,
    format_error_message,
    filtered_by_type,
)
from json_checker.core.exceptions import (
    DictCheckerError,
    FunctionCheckerError,
    ListCheckerError,
    MissKeyCheckerError,
    TypeCheckerError,
)
from json_checker.core.reports import Report


log = logging.getLogger(__name__)


def filtered_items(expected_data: dict, current_keys: list) -> Iterator:
    for k, v in expected_data.items():
        if isinstance(k, OptionalKey) and k.expected_data not in current_keys:
            log.debug("Skip %s" % k)
            continue

        if isinstance(k, OptionalKey):
            log.debug("Active %s" % k)
            k = k.expected_data
        yield (k, v)


class TypeChecker(BaseValidator):

    exception = TypeCheckerError

    def validate(self, current_data: Any) -> Report:
        """
        Examples:
        >>> from json_checker.core.reports import Report

        # If has not valid data, add to Report.errors
        >>> soft_report = Report(soft=True)
        >>> checker = TypeChecker(int, report=soft_report)
        >>> checker.validate(123)  # Report object without errors
        >>> checker.validate('123')  # Report object with errors

        # If has not valid data, raise TypeCheckerError with message
        >>> hard_report = Report(soft=False)
        >>> checker = TypeChecker(int, report=hard_report)
        >>> checker.validate(123)  # Report # object without errors
        >>> checker.validate('123')  # raise TypeCheckerError

        Must be used into `json_checker` only
        :param str | bool | int | float | type | object | None current_data:
        :return: Report
        """
        if (
            not isinstance(self.expected_data, type)
            and current_data != self.expected_data
        ):
            error = format_error_message(self.expected_data, current_data)
            self.add_or_raise(error)

        elif not isinstance(current_data, self.expected_data):
            error = format_error_message(self.expected_data, current_data)
            self.add_or_raise(error)
        return self.report


class FunctionChecker(BaseValidator):

    exception = FunctionCheckerError

    def validate(self, current_data: Any) -> Report:
        """
        Examples:
        >>> from json_checker.core.reports import Report

        # If has not valid data, add to Report.errors
        >>> soft_report = Report(soft=True)
        >>> checker = FunctionChecker(lambda x: x > 1, report=soft_report)
        >>> checker.validate(123)  # Report # object without errors
        >>> checker.validate(1)  # Report # object with errors

        # If has not valid data, raise TypeCheckerError with message
        >>> hard_report = Report(soft=False)
        >>> checker = FunctionChecker(lambda x: x > 1, report=hard_report)
        >>> checker.validate(123)  # Report object without errors
        >>> checker.validate(1)  # raise FunctionCheckerError

        Must be used into `json_checker` only
        :param any current_data:
        :return: Report
        """
        func = self.expected_data
        try:
            if not func(current_data):
                self.add_or_raise(
                    "function error: %s with data %s"
                    % (format_data(func), format_data(current_data))
                )
        except (TypeError, ValueError) as e:
            self.add_or_raise(
                "function error: %s with data %s" % (format_data(func), str(e))
            )
        return self.report


class ListChecker(BaseValidator):

    exception = ListCheckerError

    def validate(self, current_data: Iterable) -> Report:
        """
        Examples:
        >>> from json_checker.core.reports import Report

        # make different reports for examples
        >>> soft_report = Report(soft=True)
        >>> hard_report = Report(soft=False)

        # One to one with all current items
        >>> soft_checker = ListChecker([int], report=soft_report)
        >>> soft_checker.validate([1, 2, 3])  # Report object without errors
        >>> soft_checker.validate([1, '2', '3']) # Report object with 2 errors

        # One to one with all current items
        >>> hard_checker = ListChecker([int], report=hard_report)
        >>> hard_checker.validate([1, 2, 3]) # Report object without errors
        # with first error
        >>> hard_checker.validate([1, '2', '3'])  # raise TypeCheckerError

        # One to one with all current items by position
        >>> hard_checker = ListChecker([1, 2, 3], report=hard_report)
        >>> hard_checker.validate([1, 2, 3])  # Report object without errors

        # One to one with all current items by position
        >>> hard_checker = ListChecker([int, int, str], report=hard_report)
        >>> hard_checker.validate([1, 2, '3'])  # Report object without errors

        Must be used into `json_checker` only
        :param list | tuple | set | frozenset current_data:
        :return: Report
        """
        if self.expected_data == current_data:
            return self.report

        if (
            # expected [int], current 123
            (not isinstance(current_data, (list, tuple, set, frozenset)))
            or
            # expected [int], current []
            (not current_data and self.expected_data)
            or
            # expected [], current [1, 2, 3]
            (not self.expected_data and current_data)
            or
            # expected [int, str], current [1]
            (1 > len(self.expected_data) > 1)
        ):
            error = format_error_message(self.expected_data, current_data)
            return self.add_or_raise(error)

        if len(self.expected_data) == len(current_data):
            for exp, cur in list(zip(self.expected_data, current_data)):
                soft_report = Report(soft=True)
                checker = Validator(expected_data=exp, report=soft_report)
                checker.validate(cur)
                if soft_report.has_errors():
                    self.add_or_raise(str(soft_report))
            return self.report

        expected = self.expected_data[0]
        for data in current_data:
            soft_report = Report(soft=True)
            checker = Validator(expected_data=expected, report=soft_report)
            checker.validate(data)
            if soft_report.has_errors():
                self.add_or_raise(str(soft_report))
        return self.report


class DictChecker(BaseValidator):

    exception = DictCheckerError

    def validate(self, current_data: Any) -> Report:
        """
        Examples:
        >>> from json_checker.core.reports import Report

        # make simple expected schema and data for that
        >>> EXPECTED_SCHEMA = {"id": int, "name": str, "items": [int]}
        >>> right_data = {"id": 1, "name": "#1", "items": [1, 2, 3]}
        >>> broken_data = {"id": "212", "name": "#1", "items": [1, '2', '3']}

        # Soft validation:
        >>> soft_checker = DictChecker(
        >>>     EXPECTED_SCHEMA, report=Report(soft=True)
        >>> )
        >>> soft_checker.validate(right_data)  # Report object without errors
        >>> soft_checker.validate(broken_data)  # Report object with 3 errors

        # Hard validation:
        >>> hard_checker = DictChecker(
        >>>     EXPECTED_SCHEMA, report=Report(soft=False)
        >>> )
        >>> hard_checker.validate(right_data)  # Report object without errors
        # with first error, not valid `id`
        >>> hard_checker.validate(broken_data)  # raise DictCheckerError

        Must be used into `json_checker` only
        :param dict | OrderedDict current_data:
        :return: Report
        """
        if current_data == self.expected_data:
            return self.report

        if not isinstance(current_data, dict):
            message = format_error_message(dict, current_data)
            return self.add_or_raise(message)

        validated_keys = []
        current_keys = list(current_data.keys())
        for ex_key, value in filtered_items(self.expected_data, current_keys):
            if ex_key not in current_keys:
                message = "Missing keys in current response: %s" % ex_key
                self.report.add_or_raise(message, MissKeyCheckerError)
                continue

            report = Report(soft=True)
            checker = Validator(
                expected_data=value,
                report=report,
                ignore_extra_keys=self.ignore_extra_keys,
            )
            checker.validate(current_data[ex_key])
            validated_keys.append(ex_key)
            if report.has_errors():
                self.add_or_raise('From key="%s": \n\t%s' % (ex_key, report))

        if not self.ignore_extra_keys:
            miss_expected_keys = list(set(current_keys) - set(validated_keys))
            if miss_expected_keys:
                message = "Missing keys in expected schema: " "%s" % ", ".join(
                    miss_expected_keys
                )
                self.report.add_or_raise(message, MissKeyCheckerError)

        return self.report


class OptionalKey(object):
    """
    Use for not required keys into dict
    Examples:
    >>> from json_checker import Checker, TypeCheckerError

    >>> expected_schema = {'key1': int, OptionalKey('key2'): str}
    >>> checker = Checker(expected_data=expected_schema)

    # if current data have key 'key2' mast be checked else pass
    >>> checker.validate({'key1': 1}) >> {'key1': 1}
    >>> checker.validate({'key1': 1, 'key2': '2'}) >> {'key1': 1, 'key2': '2'}
    # Raise error with message
    >>> checker.validate({'key1': 1, 'key2': 2}) >> raise TypeCheckerError
    """

    def __init__(self, data: str):
        self.expected_data = data

    def __repr__(self):
        return "OptionalKey({})".format(self.expected_data)

    def __str__(self):
        return self.__repr__()


class Or(BaseOperator):
    """
    For validation some params
    even if one param must be returned True
    Examples:
    >>> from json_checker import Checker, CheckerError

    # make simple expected schema
    >>> EXPECTED_SCHEMA = {
    >>>     "id": int,
    >>>     "name": str,
    >>>     "items": Or([int], [])
    >>> }

    >>> checker = Checker(EXPECTED_SCHEMA)

    >>> checker.validate({"id": 1, "name": "test #1", "items": [1, 2, 3]})
    >>> {"id": 1, "name": "test #1", "items": [1, 2, 3]}

    >>> checker.validate({"id": 1, "name": "test #1", "items": []})
    >>> {"id": 1, "name": "test #1", "items": []}

    # raise CheckerError with error message
    >>> checker.validate({"id": 1, "name": "test #1", "items": [1, '2']})
    """

    def validate(self, current_data: Any) -> Report:
        expected = list(
            filtered_by_type(self.expected_data, type(current_data))
        )
        if not expected and self.expected_data:
            report = Report(soft=True)
            message = format_error_message(self, current_data)
            report.add("Not valid data: %s" % message)
            return report

        results = {}
        for exp_data in expected:
            report = Report(soft=True)
            checker = Validator(expected_data=exp_data, report=report)
            checker.validate(current_data)
            if not report.has_errors():
                return report
            results[len(report)] = report

        min_error = min(list(results.keys()))
        return results[min_error]


class And(BaseOperator):
    """
    from validations instance an conditions
    example:
    And(int, lambda x: 0 < x < 99)
    current data mast be checked, all conditions returned True
    Examples:
    >>> from json_checker import Checker, CheckerError

    # make simple expected schema
    >>> EXPECTED_SCHEMA = {"id": And(int, lambda x: x > 0), "name": str,}

    >>> checker = Checker(EXPECTED_SCHEMA)
    >>> checker.validate({"id": 1, "name": "test #1"})
    >>> {"id": 1, "name": "test #1"}

    >>> checker.validate({"id": -1, "name": "test #1"}) >> CheckerError
    """

    def validate(self, current_data: Any) -> Report:
        report = Report(soft=True)
        for exp_data in self.expected_data:
            checker = Validator(expected_data=exp_data, report=report)
            checker.validate(current_data)

        if report.has_errors():
            message = format_error_message(self, current_data)
            report.errors = ["Not valid data: %s" % message]
        return report


class Validator(BaseValidator):

    _validators = {
        type: TypeChecker,
        object: TypeChecker,
        type(None): TypeChecker,
        None: TypeChecker,
        int: TypeChecker,
        bool: TypeChecker,
        float: TypeChecker,
        str: TypeChecker,
        list: ListChecker,
        tuple: ListChecker,
        set: ListChecker,
        frozenset: ListChecker,
        dict: DictChecker,
        OrderedDict: DictChecker,
        FunctionType: FunctionChecker,
    }

    def validate(self, current_data: Any) -> Report:
        """

        :param any current_data:
        :return: Report
        """
        if self.expected_data == current_data:
            return self.report

        validate_method = getattr(self.expected_data, "validate", None)
        if validate_method:
            report = validate_method(current_data)
            if report and report.has_errors():
                self.report.merge(report)
            return self.report

        cls_checker = self._validators.get(type(self.expected_data))
        # TODO update report with current indent
        checker = cls_checker(
            expected_data=self.expected_data,
            ignore_extra_keys=self.ignore_extra_keys,
            report=self.report,
        )
        checker.validate(current_data)
        return self.report
