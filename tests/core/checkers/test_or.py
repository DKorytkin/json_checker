
import pytest

from json_checker.core.checkers import Or, filtered_by_type


@pytest.mark.parametrize('data, _type, expected', (
    ((int, None), type(None), [None]),
    ((int, dict, dict), type(None), []),
    ((int, dict, dict), dict, [dict, dict]),
    (({'key': int}, [int], str), dict, [{'key': int}]),
    (({'key': int}, [int], str), int, []),
    (({'key': int}, [int], str), str, [str]),
    (({'key': int}, [int], str), list, [[int]]),
    (({'key': int}, [int], str), dict, [{'key': int}])))
def test_filtered_by_type(data, _type, expected):
    assert list(filtered_by_type(data, _type)) == expected


def test_create_or_instance():
    o = Or(int, str)
    assert o.expected_data == (int, str)
    assert o.result is None


def test_create_or_instance_with_empty_param():
    o = Or()
    assert o.expected_data == tuple()
    assert o.result is None


def test_or_operator_string():
    assert str(Or(int, None)) == 'Or(int, None)'


@pytest.mark.parametrize('or_data, current_data, expected_result', [
    [(int, None), 1, None],
    [(int, ), 1, None],
    [(int, lambda x: x == 1), 1, None],
    [(int, None), None, None],
    [({'key1': int}, {'key2': str}), {'key2': 'test'}, None],
    [
        ({'key1': 1}, [{'key': str}]),
        [{'key': 'test'}],
        None
    ],
    [
        ([int, str], [int, int]),
        [1, 2],
        None
    ],
    [
        ({'key1': str}, [int]),
        [1, 2, 3],
        None
    ],
    [
        ({'key1': str}, int),
        1,
        None
    ]])
def test_operator_or(or_data, current_data, expected_result):
    assert Or(*or_data).validate(current_data) == expected_result


def test_operator_or_message():
    exp_message = "Not valid data: current value '1' (str) is not Or(int, None) (Or)"
    assert exp_message in Or(int, None).validate('1')
