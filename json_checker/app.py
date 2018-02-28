# -*- coding: utf-8 -*-

import logging
from abc import ABCMeta, abstractmethod
from functools import wraps

from six import with_metaclass

from json_checker.exceptions import (
    CheckerError,
    TypeCheckerError,
    ListCheckerError,
    DictCheckerError,
    MissKeyCheckerError
)


log = logging.getLogger(__name__)


def _is_iter(data):
    return isinstance(data, (list, tuple, set, frozenset))


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
    return _format_data(type(data))


def _format_error_message(expected_data, current_data):
    return 'current value %s is not %s' % (
        _format_data(current_data),
        _format_data(expected_data)
    )


def validation_logger(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        cls = args[0] if args else ''
        rest_args = args[1] if len(args) > 1 else ''
        log.debug('%s start with: %s %s' % (cls, rest_args, kwargs or ''))
        res = func(*args, **kwargs)
        if not res:
            log.debug('%s success' % cls)
        else:
            log.debug('%s error %s' % (cls, res))
        return res
    return wrapper


class ABCCheckerBase(with_metaclass(ABCMeta, object)):

    @abstractmethod
    def _format_errors(self):
        pass

    @abstractmethod
    def validate(self, data):
        pass

    @abstractmethod
    def __str__(self):
        pass


class BaseChecker(ABCCheckerBase):

    def __init__(self, data, soft, ignore_extra_keys=False):
        self.expected_data = data
        self.soft = soft
        self.ignore_extra_keys = ignore_extra_keys
        self.errors = []

    def __str__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            _format_data(self.expected_data)
        )

    def validate(self, data):
        pass

    def _format_errors(self):
        if self.errors:
            return '\n'.join(self.errors)


class ListChecker(BaseChecker):

    def _append_errors_or_raise(self, result):
        if result and self.soft:
            if _is_iter(result):
                self.errors.extend(result)
            else:
                self.errors.append(result)
        elif result and not self.soft:
            raise ListCheckerError(result)

    @validation_logger
    def validate(self, current_data):
        if not _is_iter(current_data):
            error = _format_error_message(self.expected_data, current_data)
            self._append_errors_or_raise(error)
            return self._format_errors()
        if self.expected_data == current_data:
            return
        if not current_data:
            error = _format_error_message(self.expected_data, current_data)
            self._append_errors_or_raise(error)
            return self._format_errors()
        if len(self.expected_data) == len(current_data):
            for ex, cu in list(zip(self.expected_data, current_data)):
                checker = Validator(ex, self.soft)
                try:
                    result = checker.validate(cu)
                except TypeCheckerError as e:
                    result = e.__str__().replace('\n', '')
                self._append_errors_or_raise(result)
            return self._format_errors()
        for checker in [Validator(d, self.soft) for d in self.expected_data]:
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
            return _format_error_message(*self.errors)

    @validation_logger
    def validate(self, current_data):
        if not isinstance(current_data, self.expected_data):
            self.errors = (self.expected_data, current_data)
            if self.soft:
                return self._format_errors()
            raise TypeCheckerError(self._format_errors())


class DictChecker(BaseChecker):

    def _append_errors_or_raise(self, key, result, exception):
        if result and isinstance(result, list):
            result = '\n\t'.join(result)
        if result and self.soft:
            self.errors.append('From key="%s": %s' % (key, result))
        elif result and not self.soft:
            raise exception('From key="%s": %s' % (key, result))

    @validation_logger
    def validate(self, data):
        if data == self.expected_data:
            return
        assert isinstance(data, dict), _format_error_message('dict', data)
        validated_keys = []
        current_keys = list(data.keys())
        for key, value in self.expected_data.items():
            if _is_optional(key) and key.expected_data not in current_keys:
                continue
            ex_key = key if not _is_optional(key) else key.expected_data
            if ex_key not in current_keys:
                message = 'Missing key'
                self._append_errors_or_raise(key, message, MissKeyCheckerError)
                continue
            current_value = data.get(ex_key)
            checker = Validator(value, self.soft, self.ignore_extra_keys)
            try:
                result = checker.validate(current_value)
            except TypeCheckerError as e:
                result = e.__str__().replace('\n', '')
            validated_keys.append(ex_key)
            self._append_errors_or_raise(key, result, DictCheckerError)
        if not self.ignore_extra_keys:
            miss_keys = set(current_keys) ^ set(validated_keys)
            message = 'Missing keys: %s' % ', '.join(miss_keys)
            if miss_keys and self.soft:
                log.debug('Added miss keys to errors')
                self.errors.append(message)
            elif miss_keys and not self.soft:
                raise MissKeyCheckerError(message)
        return self._format_errors()


class Or(ABCCheckerBase):
    """
    from validation some params
    even if one param must be returned True
    example:
    Or(int, None)
    """

    def __init__(self, *data):
        self.expected_data = data
        self.result = None

    def __str__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            [_format_data(e) for e in self.expected_data]
        )

    def _format_data(self):
        return tuple(_format_data(d) for d in self.expected_data)

    def _error_message(self, errors):
        return 'Not valid data %s%s\n%s' % (
            self.__class__.__name__,
            self._format_data(),
            '\n'.join(errors)
        )

    def _format_errors(self):
        if not self.result:
            return
        if len(self.result) == len(self.expected_data):
            return self._error_message(self.result)

    def _is_all_dicts(self, current_data):
        return bool(
            _is_dict(current_data) and
            all(_is_dict(d) for d in self.expected_data)
        )

    def _get_need_dict(self, data):
        """
        :param dict data: current dict
        :return:
        """
        dicts = {}
        current_keys = set(data.keys())
        class_name = self.__class__.__name__
        for d in self.expected_data:
            if not _is_dict(d):
                continue
            ex_dict_keys = d.keys()
            if ex_dict_keys == data.keys():
                log.debug('%s selected equals dict=%s' % (class_name, repr(d)))
                return d
            ex_keys = set()
            active_optional_count = 0
            for k in ex_dict_keys:
                if _is_optional(k) and k.expected_data not in current_keys:
                    log.debug('Skip %s' % k)
                    continue
                if _is_optional(k):
                    log.debug('Active %s' % k)
                    active_optional_count += 1
                    k = k.expected_data
                ex_keys.add(k)
            intersection_count = len(ex_keys.intersection(current_keys))
            coincide_ratio = intersection_count + active_optional_count
            dicts[coincide_ratio] = d
        log.debug('Have choice: %s' % str(dicts))
        need_dict = dicts.get(max(dicts.keys()))
        log.debug('%s selected dict=%s' % (class_name, repr(need_dict)))
        return need_dict

    @validation_logger
    def validate(self, current_data):
        if self._is_all_dicts(current_data):
            need_data = self._get_need_dict(current_data)
            validator = Validator(need_data, soft=True)
            result = validator.validate(current_data)
            if result:
                return self._error_message([result])
            return
        self.result = []
        for checker in [Validator(d, soft=True) for d in self.expected_data]:
            try:
                result = checker.validate(current_data)
            except AssertionError as e:
                result = e.__str__()
            if result:
                self.result.append(result)
        return self._format_errors()


class And(Or):
    """
    from validations instance an conditions
    example:
    And(int, lambda x: 0 < x < 99)
    current data mast be checked, all conditions returned True
    """

    def _format_errors(self):
        if self.result:
            return self._error_message(self.result)


class OptionalKey(object):
    """
    from not required keys to dict
    example:
    {'key1': 1, OptionalKey('key2'):2}
    if current data have key 'key2' mast be checked else pass
    """

    def __init__(self, data):
        self.expected_data = data
        log.debug(self.__str__())

    def __str__(self):
        return 'OptionalKey(%s)' % _format_data(self.expected_data)


class Validator(BaseChecker):

    def validate(self, data):
        if self.expected_data == data:
            return
        elif _is_iter(self.expected_data):
            list_checker = ListChecker(self.expected_data, self.soft)
            return list_checker.validate(data)
        elif _is_dict(self.expected_data):
            dict_checker = DictChecker(
                data=self.expected_data,
                soft=self.soft,
                ignore_extra_keys=self.ignore_extra_keys
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
            try:
                if not func(data):
                    return 'Function error %s' % _format_data(func)
            except TypeError as e:
                message = _format_data(func) + ' %s' % e.__str__()
                return 'Function error %s' % message
        elif self.expected_data is None:
            if self.expected_data != data:
                return _format_error_message(self.expected_data, data)
        elif self.expected_data != data:
            return _format_error_message(self.expected_data, data)


class Checker(ABCCheckerBase):

    def __init__(self, expected_data, soft=False, ignore_extra_keys=False):
        """
        :param expected_data:
        :param bool soft:
        :param bool ignore_extra_keys:
        """
        self.expected_data = expected_data
        self.ignore_extra_keys = ignore_extra_keys
        self.soft = soft
        self.result = None

    def __str__(self):
        if callable(self.expected_data):
            res = self.expected_data.__name__
        else:
            res = str(self.expected_data)
        return res

    def _format_errors(self):
        if isinstance(self.result, list):
            message = '\n'.join(self.result)
        else:
            message = self.result
        return '\n%s' % message

    def validate(self, data):
        log.debug('Checker settings: ignore_extra_keys=%s, soft=%s' % (
            self.ignore_extra_keys,
            self.soft
        ))
        checker = Validator(
            data=self.expected_data,
            soft=self.soft,
            ignore_extra_keys=self.ignore_extra_keys
        )
        self.result = checker.validate(data)
        if self.result:
            raise CheckerError(self._format_errors())
        return data
