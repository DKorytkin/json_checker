
import logging

from checker_exceptions import (
    CheckerError,
    TypeCheckerError,
    ListCheckerError,
    DictCheckerError,
    MissKeyCheckerError
)


__version__ = '1.1.3'
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


FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level='INFO')
log = logging.getLogger(__name__)


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
        log.info(u'Validation {} success'.format(self.__class__.__name__))


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
        log.info(u'Run list validation {}'.format(current_data))
        if not _is_iter(current_data):
            error = u'Current data {} is not {}'.format(
                current_data,
                SUPPORT_ITER_OBJECTS
            )
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
                    result = e.__str__().replace(u'\n', u'')
                self._append_errors_or_raise(result)
            return self._format_errors()
        for checker in [Validator(d, self.soft) for d in self.expected_data]:
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
        log.info(u'Run item validation {}'.format(current_data))
        if not isinstance(current_data, self.expected_data):
            self.errors = (self.expected_data, current_data)
            if self.soft:
                return self._format_errors()
            raise TypeCheckerError(self._format_errors())
        log.info(u'Validation TypeChecker success')


class DictChecker(BaseChecker):

    def __init__(self, data, soft, ignore):
        self.ignore = ignore
        super(DictChecker, self).__init__(data, soft)

    def _append_errors_or_raise(self, key, result, exception):
        error_message = u'From key="{}": {}'
        if result and isinstance(result, list):
            result = u'\n\t'.join(result)
        if result and self.soft:
            log.warning(u'Have error key={} result={}'.format(key, result))
            self.errors.append(error_message.format(key, result))
        elif result and not self.soft:
            log.warning(u'Have error key={} result={}'.format(key, result))
            raise exception(error_message.format(key, result))

    def validate(self, data):
        log.info(u'Run dict validation {}'.format(data))
        if data == self.expected_data:
            log.info(u'Validation DictChecker success')
            return
        assert isinstance(data, dict), u'Current data is not dict'
        validated_keys = []
        current_keys = list(data.keys())
        for key, value in self.expected_data.items():
            if _is_optional(key) and key.expected_data not in current_keys:
                continue
            ex_key = key if not _is_optional(key) else key.expected_data
            if ex_key not in current_keys:
                message = u'Missing key'
                self._append_errors_or_raise(key, message, MissKeyCheckerError)
                continue
            current_value = data.get(ex_key)
            checker = Validator(value, self.soft, self.ignore)
            try:
                result = checker.validate(current_value)
            except TypeCheckerError as e:
                result = e.__str__().replace(u'\n', u'')
            validated_keys.append(ex_key)
            self._append_errors_or_raise(key, result, DictCheckerError)
        if not self.ignore:
            miss_keys = set(current_keys) ^ set(validated_keys)
            message = u'Missing keys: {}'.format(u', '.join(miss_keys))
            if miss_keys and self.soft:
                log.warning(u'Added miss keys to errors')
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
        log.info(u'Validation Or success')

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
            keys = d.keys()
            if keys == data.keys():
                log.warning(u'{} selected equals dict={}'.format(class_name, d))
                return d
            ex_keys = set()
            active_optional_count = 0
            for k in keys:
                if _is_optional(k) and k.expected_data not in current_keys:
                    log.warning(u'Skip {}'.format(k))
                    continue
                if _is_optional(k):
                    active_optional_count += 1
                    k = k.expected_data
                ex_keys.add(k)
            intersection_count = len(ex_keys.intersection(current_keys))
            dicts[intersection_count + active_optional_count] = d
        log.warning(u'Have choice: {}'.format(dicts))
        need_dict = dicts.get(max(dicts.keys()))
        log.warning(u'{} selected dict={}'.format(class_name, need_dict))
        return need_dict

    def validate(self, current_data):
        errors = []
        log.info(u'Run {} validation {}'.format(
            self.__class__.__name__,
            current_data
        ))
        log.info(u'{} expected data {}'.format(
            self.__class__.__name__,
            self.expected_data
        ))
        if _is_dict(current_data):
            need_data = self._get_need_dict(current_data)
            validator = Validator(need_data, soft=True)
            result = validator.validate(current_data)
            if result:
                return self._error_message([result])
            return
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
        log.info(u'Validation And success')


class OptionalKey(object):
    """
    from not required keys to dict
    example:
    {'key1': 1, OptionalKey('key2'):2}
    if current data have key 'key2' mast be checked else pass
    """

    def __init__(self, data):
        self.expected_data = data
        log.info(self.__repr__())

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
        log.info(u'Checker settings: ignore_extra_keys={}, soft={}'.format(
            self.ignore_extra_keys,
            self.soft
        ))
        checker = Validator(
            expected_data=self.expected_data,
            soft=self.soft,
            ignore_extra_keys=self.ignore_extra_keys
        )
        result = checker.validate(data)
        if result:
            raise CheckerError(result)
        return data
