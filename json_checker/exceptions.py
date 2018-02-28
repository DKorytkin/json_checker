# -*- coding: utf-8 -*-


class CheckerError(Exception):
    pass


class TypeCheckerError(CheckerError):
    pass


class ListCheckerError(CheckerError):
    pass


class DictCheckerError(CheckerError):
    pass


class MissKeyCheckerError(CheckerError):
    pass
