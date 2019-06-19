json_checker
===============================================================================

.. image:: https://travis-ci.org/DKorytkin/json_checker.svg?branch=master
    :alt: Build
    :target: https://travis-ci.org/DKorytkin/json_checker

.. image:: https://codecov.io/gh/DKorytkin/json_checker/branch/master/graph/badge.svg
    :alt: Cov
    :target: https://codecov.io/gh/DKorytkin/json_checker

.. image:: https://img.shields.io/badge/python-2.7%2C%20%203.4%2C%203.5%2C%203.6-blue.svg
    :alt: Python versions
    :target: https://pypi.python.org/pypi/json_checker

.. image:: https://img.shields.io/pypi/v/json_checker.svg   
    :alt: PyPI
    :target: https://pypi.python.org/pypi/json_checker
    
**json_checker** is a library for validating Python data structures,
such as those obtained from JSON (or something else) to Python data-types.
json_checker has a parameter (soft=True) that allows you validate all json and
raise all errors after validation done, it`s very profitable from API testing:

.. code:: python

    >>> import requests
    >>>
    >>> from json_checker import Checker
    >>>
    >>>
    >>> def test_api():
    >>>     res = requests.get(API_URL).json()
    >>>     assert Checker(EXPECTED_RESPONSE, soft=True).validate(res) == res


Installation
-------------------------------------------------------------------------------

.. code-block:: sh

    $ pip install json_checker


Example
----------------------------------------------------------------------------

Here is a quick example to get a feeling of **json_checker**,
validating a list of entries with personal information:

.. code:: python

    >>> from json_checker import Checker

    >>> current_data = {'first_key': 1, 'second_key': '2'}
    >>> expected_data = {'first_key': int, 'second_key': str}


    >>> checker = Checker(expected_data)
    >>> result = checker.validate(current_data)


    >>> assert result == current_data


If data is valid, ``Checker.validate`` will return the validated data

If data is invalid, ``Checker`` will raise ``CheckerError``.


How ``json_checker`` validates data
-------------------------------------------------------------------------------

Types
~~~~~

If ``Checker(...)`` encounters a type (such as ``int``, ``str``),
it will check if the corresponding piece of data is an instance of that type,
otherwise it will raise ``CheckerError``.

.. code:: python

    >>> from json_checker import Checker

    >>> Checker(int).validate(123)
    123

    >>> Checker(int).validate('123')
    Traceback (most recent call last):
    ...
    checker_exceptions.TypeCheckerError:
    current value '123' (str) is not int


Lists, similar containers
~~~~~~~~~~~~~~~~~~~~~~~~~

If ``Checker(...)`` encounters an instance of ``list``, ``tuple``, ``set`` or
``frozenset``, it will validate contents of corresponding data container
against schemas listed inside that container:
if param ``soft`` is True validate all data,
and if have not valid data raise exception after validation

.. code:: python

    >>> Checker([int]).validate([1, 1, 0, 1])
    [1, 1, 0, 1]

    >>> Checker([str], soft=True).validate((1, 2, 3))
    Traceback (most recent call last):
    ...
    checker_exceptions.CheckerError:
    ListCheckerErrors:
    current value 1 (int) is not str
    current value 2 (int) is not str
    current value 3 (int) is not str

    >>> Checker([str]).validate((1, 2, 3))
    Traceback (most recent call last):
    ...
    checker_exceptions.ListCheckerError:
    current value 1 (int) is not str

Dictionaries
~~~~~~~~~~~~

If ``Checker(...)`` encounters an instance of ``dict``, it will validate data
key-value pairs:

.. code:: python

    >>> current_dict = {'first_key': 1, 'second_key': '2'}
    >>> checker = Checker({'first_key': int, 'second_key': int})
    >>> checker.validate(current_dict)

    Traceback (most recent call last):
    ...
    checker_exceptions.DictCheckerError:
    From key="second_key"
        current value '2' (str) is not int


Operators Or, And, OptionalKey
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you needed validate data from some conditions, use And operator
for example current data must be int instance and greater than 0 and less 99
try it:

.. code:: python

    >>> from json_checker import Checker, And

    >>> checker = Checker(And(int, lambda x: 0 < x < 99))
    >>> checker.validate(12)
    12

    >>> checker.validate(100)
    Traceback (most recent call last):
    ...
    checker_exceptions.CheckerError:
    Not valid data And(int, <lambda>),
        function error


If you need validation not required data value, use Or operator
for example current data must be int or None
try it:

.. code:: python

    >>> from json_checker import Checker, Or

    >>> checker = Checker(Or(int, None))
    >>> checker.validate(122)
    122

    >>> checker.validate('666')
    Traceback (most recent call last):
    ...
    checker_exceptions.CheckerError:
    Not valid data Or('int', None),
        current value '666' (str) is not int, current value '666' (str) is not None

If you need validate no required dict key, use OptionalKey

.. code:: python

    >>> from json_checker import Checker, OptionalKey

    >>> expected_dict = {'key1': str, OptionalKey('key2'): int}
    >>> Checker(expected_dict).validate({'key1': 'value'})
    {'key1': 'value'}

    >>> Checker(expected_dict).validate({'key1': 'value', 'key2': 'value2'})
    Traceback (most recent call last):
    ...
    checker_exceptions.DictCheckerError:
    From key="OptionalKey(key2)"
        current value 'value2' (str) is not int


More logs for debug
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> import logging
    >>> from json_checker import Checker

    >>> logging.basicConfig(level=logging.DEBUG)

    >>> Checker({'k': str}, soft=True).validate({'k': 1})
    DEBUG:json_checker.app:Checker settings: ignore_extra_keys=False, soft=True
    DEBUG:json_checker.app:DictChecker({'k': <class 'str'>} (dict)) start with: {'k': 1}
    DEBUG:json_checker.app:TypeChecker(str) start with: 1
    DEBUG:json_checker.app:TypeChecker(str) error current value 1 (int) is not str
    DEBUG:json_checker.app:DictChecker({'k': <class 'str'>} (dict)) error From key="k": current value 1 (int) is not str
    Traceback (most recent call last):
    ...
    CheckerError:
    From key="k": current value 1 (int) is not str
