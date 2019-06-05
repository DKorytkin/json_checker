

class Report:

    def __init__(self, soft=True):
        self.soft = soft
        self.errors = []

    def __str__(self):
        return '<Report soft={} {}>'.format(self.soft, self.errors)

    def __repr__(self):
        return self.__str__()

    def reset(self):
        self.errors = []
        return True

    def rebuilding(self, soft=True):
        self.soft = soft
        return self.reset()

    def add(self, error_message):
        self.errors.append(error_message)

    def add_or_rise(self, error_message, exception):
        if self.soft:
            self.add(error_message)
            return True
        raise exception

    def build(self):
        raise NotImplementedError
