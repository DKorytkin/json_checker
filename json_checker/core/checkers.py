# -*- coding: utf-8 -*-

import abc
import logging
import six
import types

from collections import OrderedDict

from json_checker.core.exceptions import (
    DictCheckerError,
    FunctionCheckerError,
    ListCheckerError,
    MissKeyCheckerError,
    TypeCheckerError,
)
from json_checker.core.reports import Report


log = logging.getLogger(__name__)


def _format_data(data):
    if callable(data):
        return data.__name__
    elif data is None:
        return repr(data)
    return '{} ({})'.format(repr(data), type(data).__name__)


def _format_error_message(expected_data, current_data):
    return 'current value %s is not %s' % (
        _format_data(current_data),
        _format_data(expected_data)
    )


def filtered_items(expected_data, current_keys):
    for k, v in expected_data.items():
        if isinstance(k, OptionalKey) and k.expected_data not in current_keys:
            log.debug('Skip %s' % k)
            continue

        if isinstance(k, OptionalKey):
            log.debug('Active %s' % k)
            k = k.expected_data
        yield (k, v)


def filtered_by_type(expected_data, _type):

    for data in expected_data:
        if isinstance(data, (_type, types.FunctionType)) or data is _type:
            yield data


class Base(six.with_metaclass(abc.ABCMeta, object)):

    def __init__(self, expected_data, soft=False, ignore_extra_keys=False):
        """
        :param any expected_data:
        :param bool soft: False by default
        :param bool ignore_extra_keys:
        """
        self.expected_data = expected_data
        self.soft = soft
        self.ignore_extra_keys = ignore_extra_keys

    def __str__(self):
        return '<%s soft=%s expected=%s>' % (
            self.__class__.__name__,
            self.soft,
            _format_data(self.expected_data)
        )

    def __repr__(self):
        return self.__str__()

    @abc.abstractmethod
    def validate(self, data):
        pass


class BaseOperator(six.with_metaclass(abc.ABCMeta, object)):

    def __init__(self, *data):
        self.expected_data = data
        self.result = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join([_format_data(e) for e in self.expected_data])
        )

    @abc.abstractmethod
    def validate(self, data):
        pass


class BaseValidator(Base):

    def __init__(self, expected_data, soft, report, ignore_extra_keys=False):
        super().__init__(expected_data, soft, ignore_extra_keys)
        self.report = report

    def _errors_or_none(self):
        if self.report.has_errors():
            return self.report
        return None

    def validate(self, current_data):
        raise NotImplementedError


class TypeChecker(BaseValidator):

    def validate(self, current_data):
        """
        Examples:
        >>> from json_checker.core.reports import Report

        # If has not valid data, add to Report.errors
        >>> soft_report = Report(soft=True)
        >>> checker = TypeChecker(int, soft=True, report=soft_report)
        >>> checker.validate(123) >> None
        >>> checker.validate('123') >> Report # object with errors

        # If has not valid data, raise TypeCheckerError with message
        >>> hard_report = Report(soft=False)
        >>> checker = TypeChecker(int, soft=False, report=hard_report)
        >>> checker.validate(123) >> None
        >>> checker.validate('123') >> raise TypeCheckerError

        Must be used into `json_checker` only
        :param str | bool | int | float | type | object | None current_data:
        :return: Report or None
        """
        if (
                not isinstance(self.expected_data, type) and
                current_data != self.expected_data
        ):
            error = _format_error_message(self.expected_data, current_data)
            self.report.add_or_rise(error, TypeCheckerError)

        elif not isinstance(current_data, self.expected_data):
            error = _format_error_message(self.expected_data, current_data)
            self.report.add_or_rise(error, TypeCheckerError)

        return self._errors_or_none()


class ListChecker(BaseValidator):

    def validate(self, current_data):
        """
        Examples:
        >>> from json_checker.core.reports import Report

        # make different reports for examples
        >>> soft_report = Report(soft=True)
        >>> hard_report = Report(soft=False)

        # One to one with all current items
        >>> soft_checker = ListChecker([int], soft=True, report=soft_report)
        >>> soft_checker.validate([1, 2, 3]) >> None
        >>> soft_checker.validate([1, '2', '3']) >> Report # object with 2 error messages

        # One to one with all current items
        >>> hard_checker = ListChecker([int], soft=False, report=hard_report)
        >>> hard_checker.validate([1, 2, 3]) >> None
        >>> hard_checker.validate([1, '2', '3']) >> raise TypeCheckerError # with first error

        # One to one with all current items by position
        >>> hard_checker = ListChecker([1, 2, 3], soft=False, report=hard_report)
        >>> hard_checker.validate([1, 2, 3]) >> None

        # One to one with all current items by position
        >>> hard_checker = ListChecker([int, int, str], soft=False, report=hard_report)
        >>> hard_checker.validate([1, 2, '3']) >> None

        Must be used into `json_checker` only
        :param list | tuple | set | frozenset current_data:
        :return: Report or None
        """
        if self.expected_data == current_data:
            return

        if (
            # expected [int], current 123
            (not isinstance(current_data, (list, tuple, set, frozenset))) or
            # expected [int], current []
            (not current_data and self.expected_data) or
            # expected [], current [1, 2, 3]
            (not self.expected_data and current_data) or
            # expected [int, str], current [1]
            (1 > len(self.expected_data) > 1)
        ):
            error = _format_error_message(self.expected_data, current_data)
            self.report.add_or_rise(error, ListCheckerError)
            return self._errors_or_none()

        if len(self.expected_data) == len(current_data):
            for expected, current in list(zip(self.expected_data, current_data)):
                checker = Validator(expected_data=expected, soft=self.soft, report=self.report)
                checker.validate(current)
            return self._errors_or_none()

        expected = self.expected_data[0]
        checker = Validator(expected_data=expected, soft=self.soft, report=self.report)
        for data in current_data:
            checker.validate(data)
        return self._errors_or_none()


class DictChecker(BaseValidator):

    def validate(self, current_data):
        """
        Examples:
        >>> from json_checker.core.reports import Report

        # make simple expected schema
        >>> EXPECTED_SCHEMA = {
        >>>     "id": int,
        >>>     "name": str,
        >>>     "items": [int]
        >>> }

        >>> soft_checker = DictChecker(EXPECTED_SCHEMA, soft=True, report=Report(soft=True))
        >>> soft_checker.validate({"id": 1, "name": "test #1", "items": [1, 2, 3]}) >> None
        >>> soft_checker.validate({
        >>>     "id": "1593977292735101516",
        >>>     "name": "test #1",
        >>>     "items": [1, '2', '3']
        >>> }) >> Report  # with 3 errors, not valid `id`, `items`

        >>> hard_checker = DictChecker(EXPECTED_SCHEMA, soft=False, report=Report(soft=False))
        >>> hard_checker.validate({"id": 1, "name": "test #1", "items": [1, 2, 3]}) >> None
        >>> hard_checker.validate({
        >>>     "id": "1:sfafasf3r1sfa",
        >>>     "name": "test #1",
        >>>     "items": [1, '2', '3']
        >>> }) >> raise DictCheckerError  # with first error, not valid `id`

        Must be used into `json_checker` only
        :param dict | OrderedDict current_data:
        :return: Report or None
        """
        if current_data == self.expected_data:
            return

        if not isinstance(current_data, dict):
            message = _format_error_message(dict, current_data)
            self.report.add_or_rise(message, DictCheckerError)
            return self._errors_or_none()

        validated_keys = []
        current_keys = list(current_data.keys())
        for ex_key, value in filtered_items(self.expected_data, current_keys):

            if ex_key not in current_keys:
                message = 'Missing keys in current response: %s' % ex_key
                self.report.add_or_rise(message, MissKeyCheckerError)
                continue

            report = Report(soft=True)
            checker = Validator(
                expected_data=value,
                soft=self.soft,
                report=report,
                ignore_extra_keys=self.ignore_extra_keys
            )
            checker.validate(current_data[ex_key])
            validated_keys.append(ex_key)
            if report.has_errors():
                message = 'From key="%s": \n\t%s' % (ex_key, report)
                self.report.add_or_rise(message, DictCheckerError)

        if not self.ignore_extra_keys:
            miss_expected_keys = list(set(current_keys) - set(validated_keys))
            if miss_expected_keys:
                message = (
                    'Missing keys in expected schema: '
                    '%s' % ', '.join(miss_expected_keys)
                )
                self.report.add_or_rise(message, MissKeyCheckerError)

        return self._errors_or_none()


class OptionalKey(object):
    """
    Use for not required keys into dict
    Examples:
    >>> from json_checker import Checker, TypeCheckerError

    >>> expected_schema = {'key1': int, OptionalKey('key2'): str}
    >>> checker = Checker(expected_data=expected_schema, soft=False)

    # if current data have key 'key2' mast be checked else pass
    >>> checker.validate({'key1': 1}) >> {'key1': 1}
    >>> checker.validate({'key1': 1, 'key2': '2'}) >> {'key1': 1, 'key2': '2'}
    >>> checker.validate({'key1': 1, 'key2': '2'}) >> raise TypeCheckerError  # with error message
    """

    def __init__(self, data):
        self.expected_data = data

    def __repr__(self):
        return 'OptionalKey({})'.format(self.expected_data)

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

    >>> checker.validate({"id": 1, "name": "test #1", "items": [1, '2']})
    >>> raise CheckerError  # with errors
    """

    def validate(self, current_data):
        expected = list(filtered_by_type(self.expected_data, type(current_data)))
        if not expected and self.expected_data:
            report = Report(soft=True)
            report.add('Not valid data: %s' % _format_error_message(self, current_data))
            return report

        results = {}
        for exp_data in expected:
            report = Report(soft=True)
            checker = Validator(expected_data=exp_data, soft=True, report=report)
            checker.validate(current_data)
            if not report.has_errors():
                return
            results[len(report)] = report

        min_error = min(list(results.keys()))
        return results[min_error]


class And(Or):
    """
    from validations instance an conditions
    example:
    And(int, lambda x: 0 < x < 99)
    current data mast be checked, all conditions returned True
    """

    def validate(self, current_data):
        report = Report(soft=True)
        for exp_data in self.expected_data:
            checker = Validator(expected_data=exp_data, soft=True, report=report)
            checker.validate(current_data)

        if report.has_errors():
            report.errors = ['Not valid data: %s' % _format_error_message(self, current_data)]
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
    }

    def validate(self, current_data):
        if self.expected_data == current_data:
            return

        validate_method = getattr(self.expected_data, 'validate', None)
        if validate_method:
            # TODO operators must returned report all time or make some for update report
            report = validate_method(current_data)
            if report and report.has_errors():
                self.report.errors.extend(report.errors)
            return self._errors_or_none()

        cls_checker = self._validators.get(type(self.expected_data))
        if cls_checker:
            # TODO update report with current indent
            checker = cls_checker(
                expected_data=self.expected_data,
                soft=self.soft,
                ignore_extra_keys=self.ignore_extra_keys,
                report=self.report,
            )
            return checker.validate(current_data)

        elif callable(self.expected_data):
            func = self.expected_data
            try:
                if not func(current_data):
                    self.report.add_or_rise(
                        'function error %s' % _format_data(func),
                        FunctionCheckerError
                    )
                    return self._errors_or_none()
            except TypeError as e:
                self.report.add_or_rise(
                    _format_data(func) + ' %s' % e.__str__(),
                    FunctionCheckerError
                )
                return self._errors_or_none()
