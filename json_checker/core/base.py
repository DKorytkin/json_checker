import abc
from types import FunctionType
from typing import Any, Iterable, Iterator, Type

from json_checker.core.reports import Report
from json_checker.core.exceptions import CheckerError


def format_data(data: Any) -> str:
    if callable(data):
        return data.__name__
    elif data is None:
        return repr(data)
    return "{} ({})".format(repr(data), type(data).__name__)


def format_error_message(expected_data: Any, current_data: Any) -> str:
    return "current value %s is not %s" % (
        format_data(current_data),
        format_data(expected_data),
    )


def filtered_by_type(expected_data: Iterable, _type: Type) -> Iterator:
    for data in expected_data:
        if isinstance(data, (_type, FunctionType)) or data is _type:
            yield data


class Base(metaclass=abc.ABCMeta):
    def __init__(
        self,
        expected_data: Any,
        soft: bool = False,
        ignore_extra_keys: bool = False,
    ):
        """
        :param any expected_data:
        :param bool soft: False by default
        :param bool ignore_extra_keys:
        """
        self.expected_data = expected_data
        self.soft = soft
        self.ignore_extra_keys = ignore_extra_keys

    def __str__(self):
        return "<%s soft=%s expected=%s>" % (
            self.__class__.__name__,
            self.soft,
            format_data(self.expected_data),
        )

    def __repr__(self):
        return self.__str__()

    @abc.abstractmethod
    def validate(self, data):
        pass


class BaseOperator(metaclass=abc.ABCMeta):
    def __init__(self, *data):
        self.expected_data = data

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join([format_data(e) for e in self.expected_data]),
        )

    @abc.abstractmethod
    def validate(self, data):
        pass


class BaseValidator(Base):

    exception = CheckerError

    def __init__(
        self,
        expected_data: Any,
        report: Report,
        ignore_extra_keys: bool = False,
    ):
        super(BaseValidator, self).__init__(
            expected_data=expected_data,
            soft=report.soft,
            ignore_extra_keys=ignore_extra_keys,
        )
        self.report = report

    def add_or_raise(self, message: str) -> Report:
        self.report.add_or_raise(message, self.exception)
        return self.report

    def validate(self, current_data):
        raise NotImplementedError
