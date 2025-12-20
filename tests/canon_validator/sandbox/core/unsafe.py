"""
Sandbox file with intentional Key 0 violation.
Key 0: No hardcoded secrets or API keys.
"""

# Key 0 Violation: Hardcoded API key
api_key = "sk-test-val-123"
AWS_SECRET = "AKIAIOSFODNN7EXAMPLE"
database_password = "SuperSecret123!"

def authenticate():
    """Uses hardcoded credentials."""
    return api_key
