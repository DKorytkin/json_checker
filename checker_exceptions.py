

class CheckerError(Exception):

    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        print(self.errors)
        return '\n{}'.format('\n'.join(
            self.errors if isinstance(self.errors, list) else [self.errors]
        ))


class TypeCheckerError(CheckerError):
    pass


class ListCheckerError(TypeCheckerError):
    pass


class DictCheckerError(TypeCheckerError):
    pass
