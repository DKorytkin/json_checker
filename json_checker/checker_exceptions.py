# -*- coding: utf-8 -*-


class CheckerError(Exception):

    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        if isinstance(self.errors, list):
            errors = '\n'.join(self.errors)
        else:
            errors = '\n'.join([self.errors])
        return '\n%s' % errors


class TypeCheckerError(CheckerError):
    pass


class ListCheckerError(CheckerError):
    pass


class DictCheckerError(CheckerError):
    pass


class MissKeyCheckerError(CheckerError):
    pass
