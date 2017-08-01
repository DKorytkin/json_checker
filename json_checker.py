

from collections import namedtuple


ERROR = namedtuple('Error', ['current_type', 'expected_type', 'current_value'])
ERROR_TEMPLATE = 'current type {}, expected type {}, current value {}'
REPR_TEMPLATE = u'{class_name}({current})'


class JsonCheckerException(Exception):

    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return '\n{}'.format('\n'.join(self.errors))


class ListValidator(object):

    def __init__(self, *args, **kwargs):
        self.data = args
        self.errors = kwargs.get('errors', [])

    def __repr__(self):
        return REPR_TEMPLATE.format(
            class_name=self.__class__.__name__,
            current=self.data
        )

    def _format_errors(self):
        if self.errors:
            return ['ListCheckerErrors:\n{}'.format('\n'.join(self.errors))]

    def validate(self, expected_data):
        for checker in [Validator(d, errors=self.errors) for d in self.data]:
            result = checker.validate(expected_data)
            if result:
                self.errors.extend(result)

        return self._format_errors()


class TypeValidator(object):

    def __init__(self, data, **kwargs):
        self.data = data
        self.errors = kwargs.get('errors', [])

    def __repr__(self):
        return REPR_TEMPLATE.format(
            class_name=self.__class__.__name__,
            current=self.data
        )

    def _format_error(self):
        if self.errors:
            errors = [ERROR_TEMPLATE.format(*e) for e in self.errors]
            return ['TypeCheckerError: {}'.format('\n'.join(errors))]

    def validate(self, expected_data):
        try:
            if not isinstance(self.data, expected_data):
                self.errors.append(
                    ERROR(type(self.data), expected_data, self.data)
                )

        except TypeError as e:
            self.errors.append(
                ERROR(type(self.data), type(expected_data), e.__str__())
            )
        return self._format_error()


class Validator(object):

    def __init__(self, current_data, errors=None):
        self.data = current_data
        self.errors = errors or []

    def __repr__(self):
        return REPR_TEMPLATE.format(
            class_name=self.__class__.__name__,
            current=self.data
        )

    def validate(self, expected_data):
        if isinstance(self.data, (list, tuple, set, frozenset)):
            list_checker = ListValidator(*self.data, errors=self.errors)
            try:
                for ex_d in expected_data:
                    return list_checker.validate(ex_d)
            except TypeError as e:
                self.errors.append(
                    'TypeError: ' + ERROR_TEMPLATE.format(
                        type(list_checker.data), expected_data, e.__str__()
                    )
                )
        elif isinstance(self.data, dict):
            pass
        elif isinstance(self.data, (str, int)):
            type_checker = TypeValidator(self.data, errors=self.errors)
            result = type_checker.validate(expected_data)
            return result

        return self.errors


class JsonChecker(object):

    def __init__(self, current_data):
        self.current_data = current_data

    def __repr__(self):
        return REPR_TEMPLATE.format(
            class_name=self.__class__.__name__,
            current=self.current_data
        )

    def validate(self, expected_data):
        checker = Validator(self.current_data)
        result = checker.validate(expected_data)
        if result:
            raise JsonCheckerException(result)
        return self.current_data
