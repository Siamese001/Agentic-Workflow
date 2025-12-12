#!/usr/bin/env python3
"""
Test file for decorator handling edge cases
"""

import os
import sys
from typing import Optional

# Test decorator before class
@dataclass
class TestClass:
    """A test class with decorator"""
    name: str
    value: int = 42

# Test multiple decorators
@staticmethod
@classmethod
def complex_function():
    """Function with multiple decorators"""
    return "complex"

# Test decorator before function with parameters
@retry(max_attempts=3)
def api_call(endpoint: str) -> Optional[dict]:
    """API call with retry decorator"""
    return {"status": "ok"}

# Test standalone decorator
def simple_decorator(func):
    """Simple decorator function"""
    return func

@simple_decorator
def decorated_function():
    """Function decorated with custom decorator"""
    pass

# Test class with decorated methods
class DecoratedClass:
    @property
    def computed_value(self) -> int:
        """Computed property"""
        return 42
    
    @classmethod
    def class_method(cls):
        """Class method"""
        return cls()
    
    @staticmethod
    def static_method():
        """Static method"""
        return "static"
