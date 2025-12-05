#!/usr/bin/env python3
"""
Comprehensive test file to validate 100% line coverage
"""

# Test imports at the beginning
import os
import sys
from typing import Optional, Dict, List
from pathlib import Path

# Global constants (should be captured as constants)
APP_NAME = "TestApp"
VERSION = "1.0.0"
DEBUG_MODE = True
MAX_RETRIES = 3

# Global assignments (should be captured as global assignments)
config_dict = {"key": "value"}
app_instance = None
supported_formats = ["json", "yaml", "xml"]

# Test class definition
class TestClass:
    """Test class with various components"""
    
    # Class constant
    CLASS_CONSTANT = "class_value"
    
    def __init__(self, name: str):
        self.name = name
    
    def instance_method(self) -> str:
        """Instance method"""
        return f"Instance: {self.name}"
    
    @classmethod
    def class_method(cls) -> str:
        """Class method"""
        return "Class method"
    
    @staticmethod
    def static_method() -> str:
        """Static method"""
        return "Static method"

# Test function definitions
def simple_function():
    """Simple function"""
    return "simple"

def function_with_params(param1: str, param2: int = 42) -> str:
    """Function with parameters"""
    return f"{param1}_{param2}"

async def async_function():
    """Async function"""
    return "async"

# Test complex expressions (should be captured as script blocks)
if __name__ == "__main__":
    # This should be captured as a script block
    print("Running comprehensive test")
    
    # Create instance
    test = TestClass("test")
    
    # Call methods
    result = test.instance_method()
    print(result)

# Test global function call at module level
print("Module loaded successfully")

# Test documentation string
"""
This is a module-level docstring that should be preserved
"""

# Test type annotations
from typing import Union

def typed_function(value: Union[str, int]) -> str:
    """Function with type annotations"""
    return str(value)

# Test error handling
try:
    risky_operation()
except Exception as e:
    error_message = f"Error: {e}"
finally:
    cleanup_code()

# Test lambda assignment
lambda_func = lambda x: x * 2

# Test list comprehension with assignment
squared_numbers = [x**2 for x in range(10)]

# Test conditional assignments
is_ready = True if config_dict else False
