# -*- coding: utf-8 -*-

import logging

from json_checker.checkers import BaseChecker, _is_func, _format_data, _format_error_message, validators, ABCCheckerBase
from json_checker.exceptions import CheckerError


log = logging.getLogger(__name__)


class Report:

    def __init__(self, soft=True):
        self._soft = soft
        self._errors = []

    def __str__(self):
        return '<Report soft={} {}>'.format(self._soft, self._errors)

    def __repr__(self):
        return self.__str__()

    def add(self, error_message):
        self._errors.append(error_message)

    def add_or_rise(self, error_message, exception):
        raise NotImplementedError


class Validator(BaseChecker):

    def validate(self, data):
        if self.expected_data == data:
            return
        # elif _is_iter(self.expected_data):
        #     list_checker = ListChecker(self.expected_data, self.soft)
        #     return list_checker.validate(data)
        # elif _is_dict(self.expected_data):
        #     dict_checker = DictChecker(
        #         data=self.expected_data,
        #         soft=self.soft,
        #         ignore_extra_keys=self.ignore_extra_keys
        #     )
        #     return dict_checker.validate(data)

        cls_checker = validators.get(type(self.expected_data))

        if cls_checker:
            checker = cls_checker(
                data=self.expected_data,
                soft=self.soft,
                ignore_extra_keys=self.ignore_extra_keys
            )
            checker.validate(data)
        # elif _is_class(self.expected_data):
        #     return self.expected_data.validate(data)
        # elif _is_type(self.expected_data):
        #     type_checker = TypeChecker(self.expected_data, self.soft)
        #     try:
        #         result = type_checker.validate(data)
        #     except TypeError as e:
        #         result = e.__str__()
        #     if result:
        #         return result
        elif _is_func(self.expected_data):
            func = self.expected_data
            try:
                if not func(data):
                    return 'function error'
            except TypeError as e:
                message = _format_data(func) + ' %s' % e.__str__()
                return 'function error %s' % message
        # TODO need check this validation
        # elif self.expected_data is None:
        #     if self.expected_data != data:
        #         return _format_error_message(self.expected_data, data)
        elif self.expected_data != data:
            return _format_error_message(self.expected_data, data)


class Checker(ABCCheckerBase):

    def __init__(self, expected_data, soft=False, ignore_extra_keys=False):
        """
        :param expected_data:
        :param bool soft:
        :param bool ignore_extra_keys:
        """
        self.expected_data = expected_data
        self.ignore_extra_keys = ignore_extra_keys
        self.soft = soft
        self.result = None

    def __str__(self):
        if callable(self.expected_data):
            res = self.expected_data.__name__
        else:
            res = str(self.expected_data)
        return res

    def _format_errors(self):
        if isinstance(self.result, list):
            message = '\n'.join(self.result)
        else:
            message = self.result
        return '\n%s' % message

    def validate(self, data):
        log.debug('Checker settings: ignore_extra_keys=%s, soft=%s' % (
            self.ignore_extra_keys,
            self.soft
        ))
        checker = Validator(
            data=self.expected_data,
            soft=self.soft,
            ignore_extra_keys=self.ignore_extra_keys
        )
        self.result = checker.validate(data)
        if self.result:
            raise CheckerError(self._format_errors())
        return data
