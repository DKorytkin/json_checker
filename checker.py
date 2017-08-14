
import json

from checker_exceptions import (
    CheckerError,
    TypeCheckerError,
    ListCheckerError,
    DictCheckerError,
)


__version__ = '1.0'
__all__ = [
    'Checker',
   'And', 'Or', 'OptionalKey',
   'CheckerError',
   'TypeCheckerError',
   'ListCheckerError',
   'DictCheckerError',
]


SUPPORT_ITER_OBJECTS = (list, tuple, set, frozenset)

NOT_SUPPORTED_ITER_OBJECT_MESSAGE = 'Current data is not {}'.format(
    SUPPORT_ITER_OBJECTS
)
ERROR_TEMPLATE = 'current value {} is not {}'
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


def _format_data(data):
    if callable(data):
        return data.__name__
    if data is None:
        return data
    return json.dumps(data)


class BaseChecker(object):

    def __init__(self, data, soft):
        self.expected_data = data
        self.soft = soft
        self.errors = []

    def _format_errors(self):
        if self.errors:
            return '{}Errors:\n{}'.format(
                self.__class__.__name__,
                '\n'.join(self.errors)
            )


class ListChecker(BaseChecker):

    def _append_errors_or_raise(self, result):
        if result and self.soft:
            if _is_iter(result):
                self.errors.extend(result)
            else:
                self.errors.append(result)
        elif result and not self.soft:
            raise ListCheckerError(result)

    def validate(self, current_data):
        for checker in [Validator(d, self.soft) for d in self.expected_data]:
            # TODO fixed [1,2,3, [4,5,6, [7,8] ,10, 11]] may be try, final
            assert _is_iter(current_data), NOT_SUPPORTED_ITER_OBJECT_MESSAGE
            for data in current_data:
                try:
                    result = checker.validate(data)
                except TypeCheckerError as e:
                    result = e.__str__().replace('\n', '')
                self._append_errors_or_raise(result)
        return self._format_errors()


class TypeChecker(BaseChecker):

    def _format_errors(self):
        if self.errors:
            return ERROR_TEMPLATE.format(*self.errors)

    def validate(self, current_data):
        if not isinstance(current_data, self.expected_data):
            self.errors = (
                _format_data(current_data),
                _format_data(self.expected_data)
            )
            if self.soft:
                return self._format_errors()
            raise TypeCheckerError(self._format_errors())


class DictChecker(BaseChecker):

    def __init__(self, data, soft, ignore):
        self.ignore = ignore
        super(DictChecker, self).__init__(data, soft)

    def _check_dicts(self, current_dict):
        assert current_dict, 'Wrong current dict is None'
        assert self.expected_data, 'Wrong expected dict is None'
        assert isinstance(current_dict, dict), 'Current data is not dict'

    def _append_errors_or_raise(self, key, result):
        if result and isinstance(result, list):
            result = '\n\t'.join(result)
        if result and self.soft:
            self.errors.append(DICT_ERROR_TEMPLATE.format(key, result))
        elif result and not self.soft:
            raise DictCheckerError(DICT_ERROR_TEMPLATE.format(key, result))

    def validate(self, data):
        self._check_dicts(data)
        validated_keys = []
        for key, value in self.expected_data.items():
            # TODO add validate key instance or equals
            if _is_optional(key) and key.expected_data not in data.keys():
                continue
            ex_key = key if not _is_optional(key) else key.expected_data
            current_value = data.get(ex_key)
            checker = Validator(value, self.soft, self.ignore)
            try:
                result = checker.validate(current_value)
            except TypeCheckerError as e:
                result = e.__str__().replace('\n', '')
            validated_keys.append(ex_key)
            self._append_errors_or_raise(key, result)
        if not self.ignore:
            miss_keys = set(data.keys()) ^ set(validated_keys)
            if miss_keys:
                message = ', '.join(miss_keys)
                self.errors.append('Missing keys: {}'.format(message))
        return self._format_errors()


class Or(object):
    """
    from validation some params
    even if one param must be returned True
    example:
    Or(int, None)
    """

    def __init__(self, *data):
        self.expected_data = data

    def __repr__(self):
        return REPR_TEMPLATE.format(
            class_name=self.__class__.__name__,
            current=self.expected_data
        )

    def _format_data(self):
        return tuple(_format_data(d) for d in self.expected_data)

    def _format_errors(self, errors):
        if len(errors) == len(self.expected_data):
            return 'Not valid data Or{}\n\t{}'.format(
                self._format_data(),
                '\n\t'.join(errors)
            )

    def validate(self, current_data):
        errors = []
        for checker in [Validator(d, soft=True) for d in self.expected_data]:
            res = checker.validate(current_data)
            if res:
                errors.append(res)
        return self._format_errors(errors)


class And(Or):
    """
    from validations instance an conditions
    example:
    And(int, lambda x: 0 < x < 99)
    current data mast be checked, all conditions returned True
    """
    def _format_errors(self, errors):
        if errors:
            return 'Not valid data And{}\n\t{}'.format(
                self._format_data(),
                '\n\t'.join(errors)
            )


class OptionalKey(object):
    """
    from not required keys to dict
    example:
    {'key1': 1, OptionalKey('key2'):2}
    if current data have key 'key2' mast be checked else pass
    """
    def __init__(self, data):
        self.expected_data = data

    def __repr__(self):
        return REPR_TEMPLATE.format(
            class_name=self.__class__.__name__,
            current=self.expected_data
        )


class Validator(object):

    def __init__(self, expected_data, soft, ignore_extra_keys=False):
        self.expected_data = expected_data
        self.soft = soft
        self.ignore_extra_keys = ignore_extra_keys
        self.errors = []

    def _append_errors(self, result):
        if result:
            self.errors.append(result)

    def validate(self, data):
        if _is_iter(self.expected_data):
            assert data and _is_iter(data), 'Wrong current data'
            list_checker = ListChecker(
                data=self.expected_data,
                soft=self.soft
            )
            result = list_checker.validate(data)
            self._append_errors(result)
        elif _is_dict(self.expected_data):
            dict_checker = DictChecker(
                data=self.expected_data,
                soft=self.soft,
                ignore=self.ignore_extra_keys
            )
            self._append_errors(dict_checker.validate(data))
        elif _is_class(self.expected_data):
            result = self.expected_data.validate(data)
            self._append_errors(result)
        elif _is_type(self.expected_data):
            type_checker = TypeChecker(
                data=self.expected_data,
                soft=self.soft
            )
            # TODO FIX TypeError: object of type 'int' has no len()
            # TODO FIX TypeError: unorderable types: str() > int()
            result = type_checker.validate(data)
            if result:
                return result
        elif _is_func(self.expected_data):
            func = self.expected_data
            try:
                if not func(data):
                    return 'Function error {}'.format(_format_data(func))
            except TypeError as e:
                return 'Function error {}'.format(
                    _format_data(func) + ' ' + e.__str__()
                )
        elif self.expected_data is None:
            if self.expected_data != data:
                return ERROR_TEMPLATE.format(
                    _format_data(data),
                    _format_data(self.expected_data)
                )
        elif self.expected_data != data:
            return ERROR_TEMPLATE.format(
                _format_data(data),
                _format_data(self.expected_data)
            )
        return self.errors


class Checker(object):

    def __init__(self, expected_data, soft=False, ignore_extra_keys=False):
        """
        :param expected_data:
        :param bool soft:
        :param bool ignore_extra_keys:
        """
        self.expected_data = expected_data
        self.ignore_extra_keys = ignore_extra_keys
        self.soft = soft

    def __repr__(self):
        res = str(self.expected_data)
        if callable(self.expected_data):
            res = self.expected_data.__name__
        return res

    def validate(self, data):
        checker = Validator(
            expected_data=self.expected_data,
            soft=self.soft,
            ignore_extra_keys=self.ignore_extra_keys
        )
        result = checker.validate(data)
        if result:
            raise CheckerError(result)
        return data
