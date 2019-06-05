import pytest

from json_checker.app import Report


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
    assert str(r) == '<Report soft=True []>'


def test_report_instance_string_with_custom_param():
    r = Report(soft=False)
    assert str(r) == '<Report soft=False []>'


def test_add_error_to_report():
    r = Report()
    r.add('test message')
    assert r.errors == ['test message']


def test_soft_add_or_rise_error_to_report():
    r = Report(soft=True)
    r.add_or_rise('test message', Exception)
    assert r.errors == ['test message']


def test_add_or_rise_error_to_report():
    r = Report(soft=False)
    with pytest.raises(KeyboardInterrupt):
        r.add_or_rise('test message', KeyboardInterrupt)


def test_build_errors():
    r = Report()
    with pytest.raises(NotImplementedError):
        r.build()
