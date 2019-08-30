import logging

from json_checker.core.exceptions import CheckerError
from json_checker.core.checkers import Base, Validator
from json_checker.core.reports import Report


log = logging.getLogger(__name__)


class Checker(Base):

    def validate(self, data):
        log.debug('Checker settings: ignore_extra_keys=%s, soft=%s' % (
            self.ignore_extra_keys,
            self.soft
        ))
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
