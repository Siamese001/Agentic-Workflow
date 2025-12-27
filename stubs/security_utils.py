"""Stub for security_utils module."""

class SecurityUtils:
    """Stub for security utility functions."""
    
    @staticmethod
    def validate_input(data: str) -> bool:
        return True
    
    @staticmethod
    def sanitize(data: str) -> str:
        return data
    
    @staticmethod
    def check_permissions(user: str, resource: str) -> bool:
        return True
    
    @staticmethod
    def encrypt(data: str) -> str:
        return f"encrypted_{data}"
    
    @staticmethod
    def decrypt(data: str) -> str:
        return data.replace("encrypted_", "")
