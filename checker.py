
import json
import inspect

from checker_exceptions import CheckerError, ListCheckerError, DictCheckerError

SUPPORT_ITER_OBJECTS = (list, tuple, set, frozenset)

NOT_SUPPORTED_ITER_OBJECT_MESSAGE = 'Current data is not {}'.format(
    SUPPORT_ITER_OBJECTS
)
ERROR_TEMPLATE = 'current type {}, expected type {}, current value {}'
DICT_ERROR_TEMPLATE = 'From key="{}"\n\t{}'
REPR_TEMPLATE = u'{class_name}({current})'


def _is_iter(data):
    return isinstance(data, SUPPORT_ITER_OBJECTS)


def _is_dict(data):
    return isinstance(data, dict)


def _is_class(data):
    return issubclass(data.__class__, (Or, And))


def _is_type(data):
    return issubclass(type(data), type)


def _is_func(data):
    return callable(data)


def _is_optional(data):
    return issubclass(data.__class__, OptionalKey)


class BaseChecker(object):

    def __init__(self, data, soft):
        self.expected_data = data
        self.soft = soft
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

    def _append_errors_or_raise(self, result):
        if result and self.soft:
            self.errors.append(result)
        elif result and not self.soft:
            raise ListCheckerError(result)

    def validate(self, current_data):
        for checker in [Validator(d, self.soft) for d in self.expected_data]:
            # TODO fixed [1,2,3, [4,5,6, [7,8] ,10, 11]] may be try, final
            assert _is_iter(current_data), NOT_SUPPORTED_ITER_OBJECT_MESSAGE
            for data in current_data:
                result = checker.validate(data)
                self._append_errors_or_raise(result)
        return self._format_errors()


class TypeChecker(BaseChecker):

    def _format_errors(self):
        if self.errors:
            error = ERROR_TEMPLATE.format(*self.errors)
            return 'TypeCheckerError: {}'.format(error)

    def validate(self, current_data):
        if not isinstance(current_data, self.expected_data):
            self.errors = (
                type(current_data),
                self.expected_data,
                json.dumps(current_data)
            )
        return self._format_errors()


class DictChecker(BaseChecker):

    def _check_dicts(self, current_dict):
        assert current_dict, 'Wrong current dict is None'
        assert self.expected_data, 'Wrong expected dict is None'
        assert isinstance(current_dict, dict), 'Current data is not dict'

    def _append_errors_or_raise(self, key, result):
        if result and self.soft:
            self.errors.append(DICT_ERROR_TEMPLATE.format(key, result))
        elif result and not self.soft:
            raise DictCheckerError(DICT_ERROR_TEMPLATE.format(key, result))

    def validate(self, data):
        self._check_dicts(data)
        for key, value in self.expected_data.items():
            checker = Validator(value, self.soft)
            # TODO add validate key instance
            # TODO add validate exist keys from expected_data
            current_value = data.get(key)
            if _is_optional(key) and key.expected_data[0] not in data.keys():
                continue
            elif _is_optional(key):
                current_value = data.get(key.expected_data[0])

            result = checker.validate(current_value)
            self._append_errors_or_raise(key, result)
        return self._format_errors()


class Or(object):
    """
    from validation some params
    even if one param must be returned True
    """

    def __init__(self, *data):
        self.expected_data = data
        self.errors = []

    def __repr__(self):
        return REPR_TEMPLATE.format(
            class_name=self.__class__.__name__,
            current=self.expected_data
        )

    def _format_errors(self):
        if len(self.errors) == len(self.expected_data):
            return '\n\t Not valid data Or{}'.format(self.expected_data)

    def validate(self, current_data):
        # TODO must be tested
        for checker in [Validator(d, soft=True) for d in self.expected_data]:
            res = checker.validate(current_data)
            if res:
                self.errors.append(res)

        return self._format_errors()


class And(Or):
    """
    from validations instance an conditions
    example:
    And(int, lambda x: 0 < x < 99)
    current data mast be checked, all conditions returned True
    """
    # TODO must be tested
    # TODO add view failed param
    def _format_errors(self):
        if self.errors:
            return '\n\t Not valid data And{}'.format(self.expected_data)


class OptionalKey(Or):
    """
    from not required keys to dict
    example:
    {'key1': 1, OptionalKey('key2'):2}
    if current data have key 'key2' mast be checked else pass
    """
    # TODO must be tested
    def __repr__(self):
        return REPR_TEMPLATE.format(
            class_name=self.__class__.__name__,
            current=self.expected_data[0]
        )


class Validator(object):

    def __init__(self, expected_data, soft):
        self.expected_data = expected_data
        self.soft = soft
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
        if _is_iter(self.expected_data):
            assert data and _is_iter(data), 'Wrong current data'
            list_checker = ListChecker(self.expected_data, self.soft)
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
            dict_checker = DictChecker(self.expected_data, self.soft)
            self._append_errors(dict_checker.validate(data))
        elif _is_class(self.expected_data):
            result = self.expected_data.validate(data)
            self._append_errors(result)
        elif _is_type(self.expected_data):
            type_checker = TypeChecker(self.expected_data, self.soft)
            # TODO FIX TypeError: object of type 'int' has no len()
            result = type_checker.validate(data)
            if result:
                return result
        elif _is_func(self.expected_data):
            func = self.expected_data
            if not func(data):
                self._append_errors('Function error {}'.format(func))
        elif self.expected_data is None:
            if self.expected_data != data:
                self._append_errors('Data is not None')
        return self.errors


class Checker(object):

    def __init__(self, expected_data, soft=False):
        self.expected_data = expected_data
        self.soft = soft

    def __repr__(self):
        res = str(self.expected_data)
        if callable(self.expected_data):
            res = inspect.getsource(self.expected_data)
        return res

    def validate(self, data):
        checker = Validator(self.expected_data, self.soft)
        result = checker.validate(data)
        if result:
            raise CheckerError(result)
        return data
