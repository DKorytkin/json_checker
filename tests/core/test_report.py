import pytest

from json_checker.core.reports import Report


def test_create_instance_with_default_params():
    r = Report()
    assert r.soft is True
    assert r.errors == []


def test_create_instance_with_custom_params():
    r = Report(soft=False)
    assert r.soft is False
    assert r.errors == []


def test_report_instance_string():
    r = Report()
    assert str(r) == ""


def test_report_instance_string_with_custom_param():
    r = Report(soft=False)
    assert str(r) == ""


def test_report_instance_string_with_errors():
    r = Report(soft=False)
    r.errors.extend(["error #1", "error #2"])
    assert str(r) == "error #1\nerror #2"


def test_add_error_to_report():
    r = Report()
    assert r.add("test message") is True
    assert r.errors == ["test message"]


def test_soft_add_or_rise_error_to_report():
    r = Report(soft=True)
    assert r.add_or_raise("test message", Exception) is True
    assert r.errors == ["test message"]


def test_add_or_rise_error_to_report():
    r = Report(soft=False)
    with pytest.raises(KeyboardInterrupt):
        r.add_or_raise("test message", KeyboardInterrupt)


def test_report_without_errors():
    r = Report(soft=True)
    assert not r.has_errors()


def test_report_has_errors():
    r = Report(soft=True)
    r.add("some error message")
    assert r.has_errors()


def test_merge_reports():
    r1 = Report()
    r1.add("some error message #1")
    r2 = Report(soft=False)
    r2.add("some error message #2")
    assert r1.merge(r2) is True
    assert r1.errors == ["some error message #1", "some error message #2"]
    assert str(r1) == "some error message #1\nsome error message #2"


def test_report_length_without_errors():
    r = Report()
    assert len(r) == 0


def test_report_length_with_errors():
    r = Report()
    r.errors.extend(["some error message #1", "some error message #2"])
    assert len(r) == 2


@pytest.mark.parametrize("exp_message", ("error", ["error"]))
def test_equal_report(exp_message):
    r = Report()
    r.add("error")
    assert r == exp_message


@pytest.mark.parametrize("exp_message", ("error", ["error"]))
def test_not_equal_report(exp_message):
    r = Report()
    r.add("some error message")
    assert r != exp_message


def test_contain_report():
    errors = ["some error message #1", "some error message #2"]
    r = Report()
    r.errors.extend(errors)
    for error in errors:
        assert error in r


def test_not_contain_report():
    r = Report()
    r.errors.extend(["some error message #1", "some error message #2"])
    assert "error" not in r
