# -*- coding: utf-8 -*-

import logging

from json_checker.core.checkers import ABCCheckerBase, Validator
from json_checker.core.exceptions import CheckerError


log = logging.getLogger(__name__)


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

    def __repr__(self):
        if callable(self.expected_data):
            res = self.expected_data.__name__
        else:
            res = str(self.expected_data)
        return '<Checker %s>' % res

    def __str__(self):
        return self.__repr__()

    def _format_errors(self):
        return '\n%s' % self.result

    def validate(self, data):
        log.debug('Checker settings: ignore_extra_keys=%s, soft=%s' % (
            self.ignore_extra_keys,
            self.soft
        ))
        checker = Validator(
            data=self.expected_data,
            soft=self.soft,
            ignore_extra_keys=self.ignore_extra_keys,
        )
        self.result = checker.validate(data)
        if self.result:
            raise CheckerError(self._format_errors())
        return data
