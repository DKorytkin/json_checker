JsonChecker
===============================================================================

**JsonChecker** is a library for validating Python data structures,
such as those obtained from JSON (or something else) to Python data-types.


Installation
-------------------------------------------------------------------------------

git clone https://github.com/DKorytkin/JsonChecker.git


Example
----------------------------------------------------------------------------

Here is a quick example to get a feeling of **json_checker**,
validating a list of entries with personal information:

.. code:: python

    >>> from json_checker import JsonChecker

    >>> current_data = {'first_key': 1, 'second_key': '2'}
    >>> expected_data = {'first_key': int, 'second_key': str}


    >>> checker = JsonChecker(current_data)
    >>> result = checker.validate(expected_data)


    >>> assert result == current_data


If data is valid, ``JsonChecker.validate`` will return the validated data

If data is invalid, ``JsonChecker`` will raise ``JsonCheckerException``.


How ``JsonChecker`` validates data
-------------------------------------------------------------------------------

Types
~~~~~

If ``JsonChecker(...)`` encounters a type (such as ``int``, ``str``),
it will check if the corresponding piece of data is an instance of that type,
otherwise it will raise ``JsonCheckerException``.

.. code:: python

    >>> from json_checker import JsonChecker

    >>> JsonChecker(123).validate(int)
    123

    >>> JsonChecker('123').validate(int)
    Traceback (most recent call last):
    ...
    JsonCheckerException:
    TypeCheckerError: current type <class 'str'>, expected type <class 'int'>, current value 123


Lists, similar containers
~~~~~~~~~~~~~~~~~~~~~~~~~

If ``JsonChecker(...)`` encounters an instance of ``list``, ``tuple``, ``set`` or
``frozenset``, it will validate contents of corresponding data container
against schemas listed inside that container:


.. code:: python

    >>> JsonChecker([1, 1, 0, 1]).validate([int])
    [1, 1, 0, 1]

    >>> JsonChecker((1, 2, 3)).validate([str])
    Traceback (most recent call last):
    ...
    json_checker.JsonCheckerException:
    ListCheckerErrors:
        TypeCheckerError: current type <class 'int'>, expected type <class 'str'>, current value 1
        TypeCheckerError: current type <class 'int'>, expected type <class 'str'>, current value 2
        TypeCheckerError: current type <class 'int'>, expected type <class 'str'>, current value 3


Dictionaries
~~~~~~~~~~~~

If ``JsonChecker(...)`` encounters an instance of ``dict``, it will validate data
key-value pairs:

.. code:: python

    >>> current_dict = {'first_key': 1, 'second_key': '2'}
    >>> checker = JsonChecker(current_dict)


    >>> checker.validate({'first_key': int, 'second_key': int})

    Traceback (most recent call last):
    ...
    json_checker.JsonCheckerException:
    DictCheckerErrors:
    From key="second_key"
    TypeCheckerError: current type <class 'str'>, expected type <class 'int'>, current value 2
