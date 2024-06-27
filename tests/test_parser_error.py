import pytest
from dateutil.parser._parser import ParserError

def test_str_with_empty_args():
    error = ParserError("")  # No format string
    assert str(error) == ""

def test_str_with_non_string_format():
    error = ParserError(42)  # Invalid format string type
    assert str(error) == "42"

def test_print_coverage():
    if not (hasattr(ParserError, 'coverage_info')):
        return
    obj = ParserError()
    print("\n")
    for key, value in obj.coverage_info.items():
        if(value == True):
            print(f"{key}:\033[32m {value}\033[0m")
        else:
            print(f"{key}:\033[31m {value}\033[0m")
        branch_coverage_percentage = sum(obj.coverage_info.values()) / len(obj.coverage_info) * 100
    if(int(branch_coverage_percentage) == 100):
        print("\nBranch coverage is \033[32m100%\033[0m")
    else:
        print(f"\nBranch coverage is \033[31m{branch_coverage_percentage}%\033[0m")
    

if __name__ == '__main__':
    pytest.main()
