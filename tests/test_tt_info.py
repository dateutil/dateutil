import pytest
from dateutil.tz.tz import _ttinfo

def test_repr_some_none():
    # Case where some attributes are None
    obj = _ttinfo()
    obj.offset = 3600
    obj.abbr = 'UTC'
    assert repr(obj) == "_ttinfo(offset=3600, abbr='UTC')"

def test_print_coverage():
    if not (hasattr(_ttinfo, 'coverage_info')):
        return
    obj = _ttinfo()
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