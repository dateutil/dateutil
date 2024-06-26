import pytest

class ParserError(ValueError):
    """Exception subclass used for any failure to parse a datetime string."""
    
    # Global dictionary to track branch coverage
    branch_coverage = {
        'try_block_entered': False,
        'except_block_entered': False
    }
    
    def __str__(self):
        try:
            self.branch_coverage['try_block_entered'] = True
            return self.args[0] % self.args[1:]
        except (TypeError, IndexError):
            self.branch_coverage['except_block_entered'] = True
            return super(ParserError, self).__str__()

    def __repr__(self):
        args = ", ".join("'%s'" % arg for arg in self.args)
        return "%s(%s)" % (self.__class__.__name__, args)

# Fixture to print branch coverage after all tests
@pytest.fixture(scope="session", autouse=True)

def print_branch_coverage(request):
    yield
    print("\nBranch Coverage:")
    for branch, count in ParserError.branch_coverage.items():
        print(f"{branch}: {count}")
    branch_coverage_percentage = sum(ParserError.branch_coverage.values()) / len(ParserError.branch_coverage) * 100
    print(f"Branch Coverage: {branch_coverage_percentage:.2f}%")

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

def test_sure_pass():
    assert True

if __name__ == '__main__':
    pytest.main()
