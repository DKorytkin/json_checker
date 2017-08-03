
import json
from collections import namedtuple


ERROR = namedtuple('Error', ['current_type', 'expected_type', 'current_value'])
ERROR_TEMPLATE = 'current type {}, expected type {}, current value {}'
DICT_ERROR_TEMPLATE = 'From key="{}"\n\t{}'
REPR_TEMPLATE = u'{class_name}({current})'
SUPPORT_ITER_OBJECTS = (list, tuple, set, frozenset)
NOT_SUPPORTED_ITER_OBJECT_MESSAGE = 'Current data is not {}'.format(
    SUPPORT_ITER_OBJECTS
)


def _is_iter(data):
    return isinstance(data, SUPPORT_ITER_OBJECTS)


def _is_dict(data):
    return isinstance(data, dict)


def _is_class(data):
    return issubclass(data, (Or, And))


def _is_type(data):
    return issubclass(type(data), type)


def _is_func(data):
    return callable(data)


class CheckerException(Exception):

    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return '\n{}'.format('\n'.join(self.errors))


class BaseChecker(object):

    def __init__(self, data):
        self.expected_data = data
        self.errors = []

    def __repr__(self):
        return REPR_TEMPLATE.format(
            class_name=self.__class__.__name__,
            current=self.expected_data
        )

    def _format_errors(self):
        if self.errors:
            return '{}Errors:\n\t{}'.format(
                self.__class__.__name__,
                '\n\t'.join(self.errors)
            )


class ListChecker(BaseChecker):

    def validate(self, current_data):
        for checker in [Validator(d) for d in self.expected_data]:
            # TODO fixed [1,2,3, [4,5,6, [7,8] ,10, 11]] may be try, final
            assert _is_iter(current_data), NOT_SUPPORTED_ITER_OBJECT_MESSAGE
            for data in current_data:
                result = checker.validate(data)
                if result:
                    self.errors.extend(result)

        return self._format_errors()


class TypeChecker(BaseChecker):

    def _format_errors(self):
        if self.errors:
            errors = [ERROR_TEMPLATE.format(*e) for e in self.errors]
            return 'TypeCheckerError: {}'.format('\n'.join(errors))

    def validate(self, current_data):
        try:
            if not isinstance(current_data, self.expected_data):
                self.errors.append(
                    ERROR(
                        type(current_data),
                        self.expected_data,
                        json.dumps(current_data)
                    )
                )

        except TypeError as e:
            self.errors.append(
                ERROR(
                    type(current_data),
                    self.expected_data,
                    e.__str__()
                )
            )
        return self._format_errors()


class DictChecker(BaseChecker):

    def _check_dicts(self, current_dict):
        assert current_dict, 'Wrong current dict is None'
        assert self.expected_data, 'Wrong expected dict is None'
        assert isinstance(current_dict, dict), 'Current data is not dict'
        check_keys = set(self.expected_data.keys()) ^ set(current_dict.keys())
        assert not check_keys, 'Difference keys {}'.format(check_keys)

    def validate(self, data):
        self._check_dicts(data)
        for key, value in self.expected_data.items():
            checker = Validator(value)
            # TODO add validate key instance
            result = checker.validate(data.get(key))
            if result:
                self.errors.append(
                    DICT_ERROR_TEMPLATE.format(key, '\n'.join(result))
                )
        return self._format_errors()


class And(BaseChecker):

    def validate(self, current_data):
        pass


class Or(BaseChecker):

    def validate(self, current_data):
        # TODO must be tested
        errors = []
        for checker in [Validator(d) for d in self.expected_data]:
            res = checker.validate(current_data)
            if res:
                errors.append(res)
        if len(errors) == len(self.expected_data):
            return errors


class Validator(object):

    def __init__(self, expected_data):
        self.expected_data = expected_data
        self.errors = []

    def __repr__(self):
        return REPR_TEMPLATE.format(
            class_name=self.__class__.__name__,
            current=self.expected_data
        )

    def _append_errors(self, result):
        if result:
            self.errors.append(result)

    def validate(self, data):
        # TODO added validation current data None
        if _is_iter(self.expected_data):
            assert data and _is_iter(data), 'Wrong current data'
            list_checker = ListChecker(self.expected_data)
            try:
                result = list_checker.validate(data)
                self._append_errors(result)
            except TypeError as e:
                self.errors.append(
                    'TypeError: ' + ERROR_TEMPLATE.format(
                        type(data),
                        type(list_checker.expected_data),
                        e.__str__()
                    )
                )
        elif _is_dict(self.expected_data):
            dict_checker = DictChecker(self.expected_data)
            self._append_errors(dict_checker.validate(data))
        elif _is_class(self.expected_data):
            # TODO added Or, And, Optional params
            checker = And(self.expected_data)
            self._append_errors(checker.validate(data))
        elif _is_type(self.expected_data):
            type_checker = TypeChecker(self.expected_data)
            self._append_errors(type_checker.validate(data))
        elif _is_func(self.expected_data):
            # TODO added validate function
            print('CALL')
            pass

        return self.errors


class Checker(object):

    def __init__(self, expected_data):
        self.expected_data = expected_data

    def __repr__(self):
        return str(self.expected_data)

    def __getattr__(self, item):
        return getattr(self.expected_data, item)

    def validate(self, data):
        checker = Validator(self.expected_data)
        result = checker.validate(data)
        if result:
            raise CheckerException(result)
        return data
