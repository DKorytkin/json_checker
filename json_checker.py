

from collections import namedtuple


ERROR = namedtuple('Error', ['current_type', 'expected_type', 'current_value'])
ERROR_TEMPLATE = 'current type {}, expected type {}, current value {}'
DICT_ERROR_TEMPLATE = 'From key="{}"\n\t{}'
REPR_TEMPLATE = u'{class_name}({current})'


class JsonCheckerException(Exception):

    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return '\n{}'.format('\n'.join(self.errors))


class BaseChecker(object):

    def __init__(self, data):
        self.data = data
        self.errors = []

    def __repr__(self):
        return REPR_TEMPLATE.format(
            class_name=self.__class__.__name__,
            current=self.data
        )

    def _format_errors(self):
        if self.errors:
            return '{}Errors:\n{}'.format(
                self.__class__.__name__,
                '\n'.join(self.errors)
            )


class ListChecker(BaseChecker):

    def validate(self, expected_data):
        for checker in [Validator(d) for d in self.data]:
            result = checker.validate(expected_data)
            if result:
                self.errors.extend(result)

        return self._format_errors()


class TypeChecker(BaseChecker):

    def _format_errors(self):
        if self.errors:
            errors = [ERROR_TEMPLATE.format(*e) for e in self.errors]
            return 'TypeCheckerError: {}'.format('\n'.join(errors))

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
        return self._format_errors()


class DictChecker(BaseChecker):

    def _check_dicts(self, expected_dict):
        assert expected_dict, 'Wrong expected dict is None'
        assert self.data, 'Wrong current dict is None'
        assert isinstance(expected_dict, dict), 'Expected data is not dict'
        check_keys = set(self.data.keys()) ^ set(expected_dict.keys())
        assert not check_keys, 'Difference keys {}'.format(check_keys)

    def validate(self, expected_data):
        self._check_dicts(expected_data)
        for key, value in self.data.items():
            checker = Validator(value)
            result = checker.validate(expected_data.get(key))
            if result:
                self.errors.append(
                    DICT_ERROR_TEMPLATE.format(key, '\n'.join(result))
                )
        return self._format_errors()


class Validator(object):

    def __init__(self, current_data):
        self.data = current_data
        self.errors = []

    def __repr__(self):
        return REPR_TEMPLATE.format(
            class_name=self.__class__.__name__,
            current=self.data
        )

    def _append_errors(self, result):
        if result:
            self.errors.append(result)

    def validate(self, expected_data):
        if isinstance(self.data, (list, tuple, set, frozenset)):
            assert expected_data, 'Wrong expected data is None'
            list_checker = ListChecker(self.data)
            try:
                for ex_d in expected_data:
                    self._append_errors(list_checker.validate(ex_d))
            except TypeError as e:
                self.errors.append(
                    'TypeError: ' + ERROR_TEMPLATE.format(
                        type(list_checker.data), expected_data, e.__str__()
                    )
                )
        elif isinstance(self.data, dict):
            dict_checker = DictChecker(self.data)
            self._append_errors(dict_checker.validate(expected_data))
        elif isinstance(self.data, (str, int)):
            type_checker = TypeChecker(self.data)
            self._append_errors(type_checker.validate(expected_data))
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
