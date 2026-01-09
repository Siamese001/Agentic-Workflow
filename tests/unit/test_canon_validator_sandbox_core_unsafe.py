import pytest
pytestmark = pytest.mark.skip(reason="DEPRECATED: Test requires external modules")

"""
Sandbox file with intentional Key 0 violation.
Key 0: No hardcoded secrets or API keys.
"""
api_key: Any = 'sk-test-val-123'
aws_secret: Any = 'AKIAIOSFODNN7EXAMPLE'
database_password: Any = 'SuperSecret123!'

def authenticate() -> Any:
    """Uses hardcoded credentials."""
    return api_key
