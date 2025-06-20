#!/usr/bin/env python

"""
Script to ensure tzutils module is properly installed

This script:
1. Checks if tzutils module is properly accessible
2. Creates proper import support if needed
3. Exits with success message if everything is working
"""

import os
import sys
from pathlib import Path

# Check if dateutil is installed
try:
    import dateutil
    print(f"Found dateutil at {dateutil.__file__}")
    print(f"Version: {dateutil.__version__}")
except ImportError:
    print("Dateutil package not found. Please install with 'pip install -e .'")
    sys.exit(1)

# Check if tzutils is accessible
try:
    from dateutil import tzutils
    print(f"tzutils module found at {tzutils.__file__}")
    print(f"Successfully imported walltimedelta: {tzutils.walltimedelta}")
    print("✅ tzutils module is properly installed!")
    sys.exit(0)
except ImportError:
    print("tzutils module not accessible yet. Adding import support...")

# Find the src directory
src_dir = Path(dateutil.__file__).parent.parent
print(f"Project src directory: {src_dir}")

# Create a simple package setup for tzutils if needed
tzutils_file = src_dir / "dateutil" / "tzutils.py"
if tzutils_file.exists():
    print(f"Found tzutils.py at {tzutils_file}")

    # Check if the module can be imported
    try:
        sys.path.insert(0, str(src_dir))
        from dateutil import tzutils
        print(f"Successfully imported tzutils after path adjustment")
    except ImportError:
        print("Still can't import tzutils. Fixing package structure...")

        # Update __init__.py to explicitly import tzutils
        init_file = src_dir / "dateutil" / "__init__.py"
        with open(init_file, 'r') as f:
            content = f.read()

        if "tzutils" not in content or "import tzutils" not in content:
            print("Updating __init__.py to import tzutils")
            new_content = content
            if "__all__" in content and "tzutils" not in content:
                new_content = content.replace("__all__ = [", "__all__ = ['tzutils', ")

            # Add import statement if not there
            if "from . import tzutils" not in new_content:
                import_pos = new_content.find("__all__")
                if import_pos > 0:
                    new_content = new_content[:import_pos] + "# Import tzutils\nfrom . import tzutils\n\n" + new_content[import_pos:]

            with open(init_file, 'w') as f:
                f.write(new_content)

            print("Updated __init__.py file. Please run 'pip install -e .' again.")

else:
    print(f"tzutils.py not found at expected location: {tzutils_file}")
    print("Please make sure the file exists")
    sys.exit(1)

print("\nPlease run 'pip install -e .' to update the installation.")
