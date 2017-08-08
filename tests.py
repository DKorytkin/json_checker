
import pytest

from checker import And, Or


OR_DATA = [
    [(int, None), 1, None],
    [(int, None), None, None],
    [(int, None), '1', "\n\t Not valid data Or('int', None)"]
]
AND_DATA = [
    [(int, lambda x: x > 0), 1, None],
    [(int, lambda x: x > 0), 0, "\n\t Not valid data And('int', '<lambda>')"],
    # [(int, lambda x: x > 0), '1', None] # TODO unskip after fix
]


@pytest.mark.parametrize('data', OR_DATA)
def test_operator_or(data):
    or_data, current_data, expected_result = data
    assert Or(*or_data).validate(current_data) == expected_result


@pytest.mark.parametrize('data', AND_DATA)
def test_operator_and(data):
    and_data, current_data, expected_result = data
    assert And(*and_data).validate(current_data) == expected_result
