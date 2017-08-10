Checker
===============================================================================

.. image:: https://travis-ci.org/DKorytkin/Checker.svg?branch=master 
    :target: https://travis-ci.org/DKorytkin/Checker
    

**Checker** is a library for validating Python data structures,
such as those obtained from JSON (or something else) to Python data-types.
Checker has a parameter (soft=True) that allows you validate all json and
raise all errors after validation done, it`s very easy API testing
Main purpose testing API


Installation
-------------------------------------------------------------------------------

pip install git+https://github.com/DKorytkin/Checker.git


Example
----------------------------------------------------------------------------

Here is a quick example to get a feeling of **checker**,
validating a list of entries with personal information:

.. code:: python

    >>> from checker import Checker

    >>> current_data = {'first_key': 1, 'second_key': '2'}
    >>> expected_data = {'first_key': int, 'second_key': str}


    >>> checker = Checker(expected_data)
    >>> result = checker.validate(current_data)


    >>> assert result == current_data


If data is valid, ``Checker.validate`` will return the validated data

If data is invalid, ``Checker`` will raise ``CheckerException``.


How ``Checker`` validates data
-------------------------------------------------------------------------------

Types
~~~~~

If ``Checker(...)`` encounters a type (such as ``int``, ``str``),
it will check if the corresponding piece of data is an instance of that type,
otherwise it will raise ``CheckerException``.

.. code:: python

    >>> from checker import Checker

    >>> Checker(int).validate(123)
    123

    >>> Checker(int).validate('123')
    Traceback (most recent call last):
    ...
    checker_exceptions.TypeCheckerError:
    current value "123" is not <class 'int'>


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
    current type <class 'int'>, expected type <class 'str'>, current value 1
    current type <class 'int'>, expected type <class 'str'>, current value 2
    current type <class 'int'>, expected type <class 'str'>, current value 3

    >>> Checker([str]).validate((1, 2, 3))
    Traceback (most recent call last):
    ...
    checker_exceptions.ListCheckerError:
    current value 1 is not <class 'str'>

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
        current value 2 is not <class 'int'>


Operators Or, And, OptionalKey
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you needed validate data from some conditions, use And operator
for example current data must be int instance and greater than 0 and less 99
try it:

.. code:: python

    >>> from checker import Checker, And

    >>> c = Checker(And(int, lambda x: 0 < x < 99))
    >>> c.validate(12)
    12

    >>> c.validate(100)
    Traceback (most recent call last):
    ...
    checker_exceptions.CheckerError:
        Not valid data And('int', '<lambda>')


If you need validation not required data value, use Or operator
for example current data must be int or None
try it:

.. code:: python

    >>> from checker import Checker, Or

    >>> c = Checker(Or(int, None))
    >>> c.validate(122)
    122

    >>> c.validate('666')
    Traceback (most recent call last):
    ...
    checker_exceptions.CheckerError:
    Not valid data Or(<class 'int'>, None)
        current value "122" is not <class 'int'>
        current value "122" is not None


If you need validate no required dict key, use OptionalKey

.. code:: python

    >>> from checker import Checker, OptionalKey

    >>> expected_dict = {'key1': str, OptionalKey('key2'): int}
    >>> Checker(expected_dict).validate({'key1': 'value'})
    {'key1': 'value'}

    >>> Checker(expected_dict).validate({'key1': 'value', 'key2': 'value2'})
    Traceback (most recent call last):
    ...
    checker_exceptions.DictCheckerError:
    From key="OptionalKey(key2)"
        current value "value2" is not <class 'int'>
