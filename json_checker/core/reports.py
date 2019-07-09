# -*- coding: utf-8 -*-


class Report:

    def __init__(self, soft=True):
        self.soft = soft
        self.errors = []

    def __repr__(self):
        return '<Report soft={} {}>'.format(self.soft, self.errors)

    def __str__(self):
        return '\n'.join(self.errors)

    def __len__(self):
        return len(self.errors)

    def __eq__(self, other):
        return self.__str__() == other

    def __add__(self, other):
        return self.__str__() + str(other)

    def __contains__(self, item):
        return item in self.__str__()

    def has_errors(self):
        return bool(self.errors)

    def add(self, error_message):
        self.errors.append(error_message)

    def add_or_rise(self, error_message, exception):
        if self.soft:
            self.add(error_message)
            return True
        raise exception(error_message)
