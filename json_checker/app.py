# -*- coding: utf-8 -*-

import logging

from json_checker.checkers import ABCCheckerBase, Validator
from json_checker.exceptions import CheckerError


log = logging.getLogger(__name__)


class Report:

    def __init__(self, soft=True):
        self.soft = soft
        self.errors = []

    def __str__(self):
        return '<Report soft={} {}>'.format(self.soft, self.errors)

    def __repr__(self):
        return self.__str__()

    def add(self, error_message):
        self.errors.append(error_message)

    def add_or_rise(self, error_message, exception):
        if self.soft:
            self.add(error_message)
            return True
        raise exception

    def build(self):
        raise NotImplementedError


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
        self.report = Report(self.soft)

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
