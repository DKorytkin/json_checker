import logging

from typing import Any

from json_checker.core.base import Base
from json_checker.core.exceptions import CheckerError
from json_checker.core.checkers import Validator
from json_checker.core.reports import Report


log = logging.getLogger(__name__)


class Checker(Base):
    def validate(self, data: Any) -> Any:
        log.debug(
            "Checker settings: ignore_extra_keys=%s, soft=%s"
            % (self.ignore_extra_keys, self.soft)
        )
        report = Report(self.soft)
        checker = Validator(
            expected_data=self.expected_data,
            report=report,
            ignore_extra_keys=self.ignore_extra_keys,
        )
        checker.validate(data)
        if report.has_errors():
            raise CheckerError(report)
        return data
