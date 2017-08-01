

REPR_TEMPLATE = u'{class_name}({current})'


def _is_list(t):
    return isinstance(t, (list, tuple, set, frozenset))


class ListValidator(object):

    def __init__(self, *args, **kwargs):
        self.data = args
        self.errors = kwargs.get('errors', [])

    def __repr__(self):
        return REPR_TEMPLATE.format(
            class_name=self.__class__.__name__,
            current=self.data
        )

    def validate(self, expected_data):
        for checker in [Validator(d) for d in self.data]:
            try:
                checker.validate(expected_data)
            # TODO fix exception
            except Exception as e:
                self.errors.append(e)

        return self.errors


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
        if not isinstance(self.data, expected_data):
            raise TypeError(self.data, expected_data)

        if _is_list(self.data):
            list_checker = ListValidator(*self.data, errors=self.errors)
            return list_checker.validate(expected_data)
        elif isinstance(self.data, dict):
            return self.data

        if self.errors:
            return self.errors


class JsonChecker(object):

    def __init__(self, current_data):
        self.current_data = current_data

    def validate(self, expected_data):
        checker = Validator(self.current_data)
        result = checker.validate(expected_data)
        if result:
            # TODO fix exception
            raise Exception(result)
