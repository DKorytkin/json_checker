
import pytest

from json_checker import Checker, And, Or, OptionalKey


OR_DATA = [
    [(int, None), 1, None],
    [(int, None), None, None]
]
AND_DATA = [
    [(int, lambda x: x > 0), 1, None],
    [(int, bool), True, None]
]
AND_DATA_MESSAGE = [
    [(int, bool), 0],
    [(int, lambda x: x > 0), 0],
    [(int, lambda x: x > 0), '1']
]
OPTIONAL_DATA = [
    [{OptionalKey('key'): 'value'}, {'key': 'value'}, {'key': 'value'}],
    [{OptionalKey('key'): 'value'}, {}, {}],
    [
        {OptionalKey('key'): 'value', 'key2': 'value2'},
        {'key2': 'value2'},
        {'key2': 'value2'}
    ]
]
OPERATOR_CLASS_DATA = [
    [Or, 1, "Or(['int'])"],
    [And, 1, "And(['int'])"],
    [OptionalKey, 'test', 'OptionalKey(str)'],
]
TEST_DICT = {OptionalKey('key2'): str, 'test': int}
TEST_OPTION_DICT = {
    'key1': int,
    OptionalKey('key2'): str,
    OptionalKey('key3'): bool
}
TEST_LARGE_DICT = {
    OptionalKey('key1'): str,
    'key2': bool,
    OptionalKey('key3'): str,
    'key4': bool,
    'key5': str,
    OptionalKey('key6'): str,
    OptionalKey('key7'): str,
    OptionalKey('key8'): str,
    OptionalKey('key9'): bool,
    OptionalKey('key10'): Or([str], [])
}
OPERATOR_OR_DICT_DATA = [
    [({'key1': 1}, {'key2': str}), {'key2': 'test'}, {'key2': str}],
    [({'key1': 1}, {'key2': str}), {'key1': 'test'}, {'key1': 1}],
    [({'key1': 1}, [str]), {'key1': 1, 'key2': 'test'}, {'key1': 1}],
    [({'key1': 1, 'test': int}, TEST_DICT), {'test': 2}, TEST_DICT],
    [(TEST_OPTION_DICT, {'test': 1}), {'key2': 1}, TEST_OPTION_DICT],
    [(TEST_OPTION_DICT, {'test': 1}), {}, {'test': 1}],
    [(TEST_OPTION_DICT, {'test': 1}), {'test': 2}, {'test': 1}],
    [(TEST_OPTION_DICT, {}), {}, {}],
    [
        (TEST_LARGE_DICT, {}),
        {
            'key10': [],
            'key8': 'test text',
            'key9': False,
            'key6': '11.07.2014',
            'key4': True,
            'key3': 'by_dates',
            'key1': '18.07.2014'
        },
        TEST_LARGE_DICT
    ],
    [
        ({'key1': 1, 'test': 2}, {'key2': str, 'test': 2}),
        {'key1': 'test', 'test': 2},
        {'key1': 1, 'test': 2}
    ],
    [
        ({'key1': 1}, {'key2': str, 'key1': int, 'key3': bool}),
        {'key1': 'test'},
        {'key1': 1}
    ]
]


@pytest.mark.parametrize('data', OR_DATA)
def test_operator_or(data):
    or_data, current_data, expected_result = data
    assert Or(*or_data).validate(current_data) == expected_result


def test_operator_or_message():
    assert 'Not valid data Or' in Or(int, None).validate('1')


@pytest.mark.parametrize('data', AND_DATA)
def test_operator_and(data):
    and_data, current_data, expected_result = data
    assert And(*and_data).validate(current_data) == expected_result


@pytest.mark.parametrize('data', AND_DATA_MESSAGE)
def test_operator_and(data):
    and_data, current_data = data
    assert 'Not valid data And' in And(*and_data).validate(current_data)


@pytest.mark.parametrize('data', OPTIONAL_DATA)
def test_operator_optional_key(data):
    optional_data, current_data, expected_result = data
    assert Checker(optional_data).validate(current_data) == expected_result


@pytest.mark.parametrize('data', OPERATOR_CLASS_DATA)
def test_repr_operator_class(data):
    data_class, test_data, expected_result = data
    c = data_class(test_data)
    assert c.__str__() == expected_result


@pytest.mark.parametrize('data', OPERATOR_OR_DICT_DATA)
def test_operator_or_need_dict(data):
    or_data, current_data, expected_data = data
    validator = Or(*or_data)
    assert validator._get_need_dict(current_data) == expected_data
