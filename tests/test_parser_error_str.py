import pytest
from dateutil.parser._parser import ParserError

def test_str_with_valid_format():
    error = ParserError("Parsing failed: %s, %d", "reason", 42)
    assert str(error) == "Parsing failed: reason, 42"

def test_str_with_no_args():
    error = ParserError("Parsing failed")
    assert str(error) == "Parsing failed"

def test_str_with_empty_args():
    error = ParserError("")  # No format string
    assert str(error) == ""

def test_str_with_non_string_format():
    error = ParserError(42)  # Invalid format string type
    assert str(error) == "42"

def test_str_with_type_error():
    error = ParserError("Parsing failed: %s, %d")  # Format string without placeholders
    assert str(error) == "Parsing failed: %s, %d"


if __name__ == '__main__':
    pytest.main()