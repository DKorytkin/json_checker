import abc
import datetime
import re

from typing import Union, Dict

from json_checker.core.base import format_error_message
from json_checker.core.reports import Report


URL_BASE_PATTERN = r"^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"
EMAIL_BASE_PATTERN = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
IP_ADDRESS_BASE_PATTERN = (
    r"^(([0-9]|[1-9][0-9]|1[0-9]{2}"
    r"|2[0-4][0-9]|25[0-5])\.){3}"
    r"([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
)
MAC_ADDRESS_BASE_PATTERN = r"^[a-fA-F0-9:]{17}|[a-fA-F0-9]{12}$"


def is_float(number: Union[int, str, float]) -> bool:
    try:
        float(number)
        return True
    except ValueError:
        return False


class BaseType(metaclass=abc.ABCMeta):

    types = (type(None), )

    def __str__(self):
        return f"<{self.__class__.__name__}>"

    def __repr__(self):
        return self.__str__()

    @property
    def report(self):
        report = getattr(self, "__report", None)
        if report is None:
            report = Report(soft=True)
            setattr(self, "__report", report)
        return report

    @report.setter
    def report(self, instance: Report):
        """
        For tests only!!!
        :param Report instance:
        """
        setattr(self, "__report", instance)

    def _validate_instance(self, value) -> Report:
        """
        Validate value on equals expected type
        :param any value:
        :return: Report
        """
        if not isinstance(value, self.types):
            self.report.add(format_error_message(self.types, value))
        return self.report

    def _validate_boundaries(self, number) -> Report:
        """
        The values of boundaries validate only if exist attributes: min, max
        :param int number:
        :return: Report
        """
        _min = getattr(self, "min", None)
        if _min and number <= _min:
            self.report.add(f"current value {number} <= {_min}")

        _max = getattr(self, "max", None)
        if _max and number >= _max:
            self.report.add(f"current value {number} >= {_max}")
        return self.report

    @abc.abstractmethod
    def validate(self, x) -> Report:
        raise NotImplementedError

    @abc.abstractmethod
    def to_json(self) -> Dict[str, str]:
        raise NotImplementedError


class Int(BaseType):

    types = (int, )
    json_class = "number"

    def __init__(self, min_number: int = None, max_number: int = None):
        self.min = min_number
        self.max = max_number

    def validate(self, number) -> Report:
        self._validate_instance(number)
        self._validate_boundaries(number)
        return self.report

    def to_json(self):
        return {"type": self.json_class, "min": self.min, "max": self.max}


class Float(Int):

    types = (float, )


class Number(Int):

    types = (float, int)

    def validate(self, number) -> Report:
        if isinstance(number, str):
            if number.isdigit():
                number = int(number)
            elif is_float(number):
                number = float(number)
            else:
                self.report.add(format_error_message(self.types, number))
                return self.report

        self._validate_instance(number)
        self._validate_boundaries(number)
        return self.report


class Str(BaseType):

    types = (str, )
    json_class = "string"

    def __init__(self, min_length: int = None, max_length: int = None, regexp_pattern: str = None):
        self.min = min_length
        self.max = max_length
        self.regexp_pattern = regexp_pattern

    def validate(self, value: str) -> Report:
        self._validate_instance(value)
        self._validate_boundaries(len(value))
        if self.regexp_pattern:
            report = Regex(self.regexp_pattern).validate(value)
            self.report.merge(report)
        return self.report

    def to_json(self):
        return {
            "type": self.json_class,
            "max": self.max,
            "min": self.min,
            "pattern": self.regexp_pattern
        }


class Regex(BaseType):
    types = (str, )
    json_class = "string"
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

    @property
    def flag(self) -> int:
        for f_name, f_index in self.flags:
            if isinstance(self._flag, str) and self._flag == f_name:
                return f_index
            elif isinstance(self._flag, int) and self._flag == f_index:
                return self._flag
        raise Exception(f"Not supported flag: {self._flag}")

    def validate(self, string) -> Report:
        self._validate_instance(string)
        if re.search(self.pattern, string, self.flag):
            return self.report
        self.report.add(f"Not valid data: '{string}' ({self.pattern})")
        return self.report

    def to_json(self):
        return {"type": self.json_class, "pattern": self.pattern, "flag": self.flag}


class Url(Regex):

    def __init__(self, pattern: str = URL_BASE_PATTERN, flag=0):
        super(Url, self).__init__(pattern, flag)


class Email(Regex):

    def __init__(self, pattern: str = EMAIL_BASE_PATTERN, flag=0):
        super(Email, self).__init__(pattern, flag)


class IPAddress(Regex):

    def __init__(self, pattern: str = IP_ADDRESS_BASE_PATTERN, flag=0):
        super(IPAddress, self).__init__(pattern, flag)


class MACAddress(Regex):

    def __init__(self, pattern: str = MAC_ADDRESS_BASE_PATTERN, flag=0):
        super(MACAddress, self).__init__(pattern, flag)


class Date(BaseType):

    types = (str, )
    json_type = "date"

    def __init__(self, data_format="%Y-%m-%d"):
        self.data_format = data_format

    def validate(self, value) -> Report:
        self._validate_instance(value)
        try:
            date_class = getattr(datetime, self.json_type)
            date_class.fromisoformat(self.data_format)
        except ValueError as error:
            self.report.add(error)
        return self.report

    def to_json(self):
        return {"type": self.json_type, "format": self.data_format}


class DateTime(Date):

    json_type = "datetime"

    def __init__(self, data_format="%Y-%m-%dT%H:%M:%SZ"):
        super(DateTime, self).__init__(data_format)


class Array(BaseType):

    types = (list, tuple, set, frozenset)
    json_type = "array"

    def __init__(self, data, min_length: int = None, max_length: int = None):
        self.data = data
        self.min = min_length
        self.max = max_length

    def validate(self, current_data) -> Report:
        self._validate_instance(current_data)
        self._validate_boundaries(len(current_data))
        # TODO add more validation and tests
        return self.report

    def to_json(self) -> Dict[str, str]:
        return {"type": self.json_type, "min": self.min, "max": self.max}
