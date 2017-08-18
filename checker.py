
from checker_exceptions import (
    CheckerError,
    TypeCheckerError,
    ListCheckerError,
    DictCheckerError,
    MissKeyCheckerError
)


__version__ = '1.0.2'
__all__ = [
    'Checker',
    'And',
    'Or',
    'OptionalKey',
    'CheckerError',
    'TypeCheckerError',
    'ListCheckerError',
    'DictCheckerError',
    'MissKeyCheckerError'
]


SUPPORT_ITER_OBJECTS = (list, tuple, set, frozenset)


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
    return repr(data)


def _format_error_message(expected_data, current_data):
    return u'current value {} is not {}'.format(
        _format_data(current_data),
        _format_data(expected_data)
    )


class BaseChecker(object):

    def __init__(self, data, soft):
        self.expected_data = data
        self.soft = soft
        self.errors = []

    def _format_errors(self):
        if self.errors:
            return u'\n'.join(self.errors)


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
        if self.expected_data == current_data:
            return
        for checker in [Validator(d, self.soft) for d in self.expected_data]:
            # TODO fixed [1,2,3, [4,5,6, [7,8] ,10, 11]] may be try, final
            # TODO validate position on list [int, str, bool]
            if not current_data:
                self._append_errors_or_raise(
                    _format_error_message(self.expected_data, current_data)
                )
            for data in current_data:
                try:
                    result = checker.validate(data)
                except TypeCheckerError as e:
                    result = e.__str__().replace(u'\n', u'')
                self._append_errors_or_raise(result)
        return self._format_errors()


class TypeChecker(BaseChecker):

    def _format_errors(self):
        if self.errors:
            return _format_error_message(*self.errors)

    def validate(self, current_data):
        if not isinstance(current_data, self.expected_data):
            self.errors = (self.expected_data, current_data)
            if self.soft:
                return self._format_errors()
            raise TypeCheckerError(self._format_errors())


class DictChecker(BaseChecker):

    def __init__(self, data, soft, ignore):
        self.ignore = ignore
        super(DictChecker, self).__init__(data, soft)

    def _check_dicts(self, current_dict):
        assert current_dict, u'Wrong current dict is None'
        assert self.expected_data, u'Wrong expected dict is None'
        assert isinstance(current_dict, dict), u'Current data is not dict'

    def _append_errors_or_raise(self, key, result):
        error_message = u'From key="{}": {}'
        if result and isinstance(result, list):
            result = u'\n\t'.join(result)
        if result and self.soft:
            self.errors.append(error_message.format(key, result))
        elif result and not self.soft:
            raise DictCheckerError(error_message.format(key, result))

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
                result = e.__str__().replace(u'\n', u'')
            validated_keys.append(ex_key)
            self._append_errors_or_raise(key, result)
        if not self.ignore:
            miss_keys = set(data.keys()) ^ set(validated_keys)
            message = u'Missing keys: {}'.format(u', '.join(miss_keys))
            if miss_keys and self.soft:
                self.errors.append(message)
            elif miss_keys and not self.soft:
                raise MissKeyCheckerError(message)
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
        return u'{class_name}{data}'.format(
            class_name=self.__class__.__name__,
            data=self.expected_data
        )

    def _format_data(self):
        return tuple(_format_data(d) for d in self.expected_data)

    def _error_message(self, errors):
        return u'Not valid data {}{}\n{}'.format(
            self.__class__.__name__,
            self._format_data(),
            u'\n\t'.join(errors)
        )

    def _format_errors(self, errors):
        if len(errors) == len(self.expected_data):
            return self._error_message(errors)

    def _get_need_dict(self, data):
        """
        :param dict data: current dict
        :return:
        """
        dicts = {}
        current_keys = set(data.keys())
        for d in self.expected_data:
            if not _is_dict(d):
                continue
            ex_keys = set()
            for k in d.keys():
                if _is_optional(k) and k.expected_data not in data.keys():
                    continue
                ex_keys.add(k)
            dicts[len(ex_keys ^ current_keys)] = d
        return dicts.get(min(dicts.keys()))

    def validate(self, current_data):
        errors = []
        if _is_dict(current_data):
            need_data = self._get_need_dict(current_data)
            assert need_data, u'Wrong data'
            validator = Validator(need_data, soft=True)
            result = validator.validate(current_data)
            if result:
                return self._error_message([result])
        for checker in [Validator(d, soft=True) for d in self.expected_data]:
            try:
                result = checker.validate(current_data)
            except AssertionError as e:
                result = e.__str__()
            if result:
                errors.append(result)
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
            return self._error_message(errors)


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
        return u'OptionalKey({})'.format(self.expected_data)


class Validator(object):

    def __init__(self, expected_data, soft, ignore_extra_keys=False):
        self.expected_data = expected_data
        self.soft = soft
        self.ignore_extra_keys = ignore_extra_keys

    def __repr__(self):
        return u'Validator({})'.format(self.expected_data)

    def validate(self, data):
        if _is_iter(self.expected_data):
            error = u'Current data is not {}'.format(SUPPORT_ITER_OBJECTS)
            assert _is_iter(data), error
            list_checker = ListChecker(self.expected_data, self.soft)
            return list_checker.validate(data)
        elif _is_dict(self.expected_data):
            dict_checker = DictChecker(
                data=self.expected_data,
                soft=self.soft,
                ignore=self.ignore_extra_keys
            )
            return dict_checker.validate(data)
        elif _is_class(self.expected_data):
            return self.expected_data.validate(data)
        elif _is_type(self.expected_data):
            type_checker = TypeChecker(self.expected_data, self.soft)
            try:
                result = type_checker.validate(data)
            except TypeError as e:
                result = e.__str__()
            if result:
                return result
        elif _is_func(self.expected_data):
            func = self.expected_data
            error_message = u'Function error {}'
            try:
                if not func(data):
                    return error_message.format(_format_data(func))
            except TypeError as e:
                return error_message.format(
                    _format_data(func) + u' {}'.format(e.__str__())
                )
        elif self.expected_data is None:
            if self.expected_data != data:
                return _format_error_message(self.expected_data, data)
        elif self.expected_data != data:
            return _format_error_message(self.expected_data, data)


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
