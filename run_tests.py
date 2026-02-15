import sys

sys.path.insert(0, '.')
import pytest

sys.exit(pytest.main(["-v", "tests/enforcement/test_constitutional_validator.py"]))
