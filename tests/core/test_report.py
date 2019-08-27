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
    r.errors = ["error #1", "error #2"]
    assert str(r) == "error #1\nerror #2"


def test_add_error_to_report():
    r = Report()
    r.add("test message")
    assert r.errors == ["test message"]


def test_soft_add_or_rise_error_to_report():
    r = Report(soft=True)
    r.add_or_rise("test message", Exception)
    assert r.errors == ["test message"]


def test_add_or_rise_error_to_report():
    r = Report(soft=False)
    with pytest.raises(KeyboardInterrupt):
        r.add_or_rise("test message", KeyboardInterrupt)
