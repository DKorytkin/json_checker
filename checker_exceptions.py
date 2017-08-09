

class CheckerError(Exception):

    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return '\n{}'.format('\n'.join(
            self.errors if isinstance(self.errors, list) else [self.errors]
        ))


class ListCheckerError(CheckerError):
    pass


class DictCheckerError(CheckerError):
    pass
