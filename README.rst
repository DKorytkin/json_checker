Checker
===============================================================================

**Checker** is a library for validating Python data structures,
such as those obtained from JSON (or something else) to Python data-types.


Installation
-------------------------------------------------------------------------------

git clone https://github.com/DKorytkin/JsonChecker.git


Example
----------------------------------------------------------------------------

Here is a quick example to get a feeling of **checker**,
validating a list of entries with personal information:

.. code:: python

    >>> from checker import Checker

    >>> current_data = {'first_key': 1, 'second_key': '2'}
    >>> expected_data = {'first_key': int, 'second_key': str}


    >>> checker = Checker(current_data)
    >>> result = checker.validate(expected_data)


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

    >>> Checker(123).validate(int)
    123

    >>> Checker('123').validate(int)
    Traceback (most recent call last):
    ...
    CheckerException:
    TypeCheckerError: current type <class 'str'>, expected type <class 'int'>, current value 123


Lists, similar containers
~~~~~~~~~~~~~~~~~~~~~~~~~

If ``Checker(...)`` encounters an instance of ``list``, ``tuple``, ``set`` or
``frozenset``, it will validate contents of corresponding data container
against schemas listed inside that container:


.. code:: python

    >>> Checker([1, 1, 0, 1]).validate([int])
    [1, 1, 0, 1]

    >>> Checker((1, 2, 3)).validate([str])
    Traceback (most recent call last):
    ...
    checker.CheckerException:
    ListCheckerErrors:
        TypeCheckerError: current type <class 'int'>, expected type <class 'str'>, current value 1
        TypeCheckerError: current type <class 'int'>, expected type <class 'str'>, current value 2
        TypeCheckerError: current type <class 'int'>, expected type <class 'str'>, current value 3


Dictionaries
~~~~~~~~~~~~

If ``Checker(...)`` encounters an instance of ``dict``, it will validate data
key-value pairs:

.. code:: python

    >>> current_dict = {'first_key': 1, 'second_key': '2'}
    >>> checker = Checker(current_dict)


    >>> checker.validate({'first_key': int, 'second_key': int})

    Traceback (most recent call last):
    ...
    checker.CheckerException:
    DictCheckerErrors:
    From key="second_key"
    TypeCheckerError: current type <class 'str'>, expected type <class 'int'>, current value 2
