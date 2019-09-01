import abc
import re

from typing import Union

from json_checker.core.base import format_error_message
from json_checker.core.reports import Report


def is_float(number: Union[int, str, float]) -> bool:
    try:
        float(number)
        return True
    except ValueError:
        return False


class BaseType(metaclass=abc.ABCMeta):

    def __str__(self):
        return f"<{self.__class__.__name__}>"

    def __repr__(self):
        return self.__str__()

    @abc.abstractmethod
    def validate(self, x) -> Report:
        raise NotImplementedError


class Int(BaseType):

    types = (int, )

    def __init__(self, min_number: int = None, max_number: int = None):
        self.min = min_number
        self.max = max_number
        self.report = Report()

    def validate(self, number) -> Report:
        if not isinstance(number, self.types):
            self.report.add(format_error_message(self.types, number))
            return self.report

        if self.min and number < self.min:
            self.report.add(f"current value {number} < {self.min}")

        if self.max and number > self.max:
            self.report.add(f"current value {number} > {self.max}")

        return self.report


class Float(Int):

    types = (float, )


class Number(BaseType):

    types = (float, int)

    def __init__(self, min_number: int = None, max_number: int = None):
        self.min = min_number
        self.max = max_number
        self.report = Report()

    def validate(self, number) -> Report:
        if isinstance(number, str):
            if number.isdigit():
                number = int(number)
            elif is_float(number):
                number = float(number)
            else:
                self.report.add(format_error_message(self.types, number))
                return self.report

        if not isinstance(number, self.types):
            self.report.add(format_error_message(self.types, number))
            return self.report

        if self.min and number < self.min:
            self.report.add(f"current value {number} < {self.min}")

        if self.max and number > self.max:
            self.report.add(f"current value {number} > {self.max}")

        return self.report


class Str(BaseType):

    types = (str, )

    def __init__(self, min_length: int = None, max_length: int = None, regexp: str = None):
        self.min = min_length
        self.max = max_length
        self.report = Report()

    def validate(self, value: str) -> Report:
        if not isinstance(value, self.types):
            self.report.add(format_error_message(self.types, value))
            return self.report

        length = len(value)
        if self.min and length < self.min:
            self.report.add(f"current length of value {length} < {self.min}")

        if self.max and length > self.max:
            self.report.add(f"current length of value {length} > {self.max}")

        return self.report


class Regex(BaseType):

    flags = (
        ("ASCII", re.ASCII),
        ("DEBUG", re.DEBUG),
        ("VERBOSE", re.VERBOSE),
        ("UNICODE", re.UNICODE),
        ("DOTALL", re.DOTALL),
        ("MULTILINE", re.MULTILINE),
        ("LOCALE", re.LOCALE),
        ("IGNORECASE", re.IGNORECASE),
        ("TEMPLATE", re.TEMPLATE),
    )

    def __init__(self, pattern: str, flag=0):
        self.pattern = pattern
        self._flag = flag
        self.report = Report()

    @property
    def flag(self) -> int:
        for f_name, f_index in self.flags:
            if isinstance(self._flag, str) and self._flag == f_name:
                return f_index
            elif isinstance(self._flag, int) and self._flag == f_index:
                return self._flag
        raise Exception(f"Not supported flag: {self._flag}")

    def validate(self, string) -> Report:
        if re.search(self.pattern, string, self.flag):
            return self.report
        self.report.add(f"Not valid data: '{string}' ({self.pattern})")
        return self.report


class Url(Regex):

    def __init__(self, pattern: str = r"", flag=0):
        super(Url, self).__init__(pattern, flag)
