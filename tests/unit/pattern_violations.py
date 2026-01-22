"""
Pattern Violation Test Fixture

This file contains various coding pattern violations that the
CodeStandardsEnforcerAgent should detect.

DO NOT FIX - Used for testing pattern enforcement.
"""


import builtins


# VIOLATION Key 26: Mutable default argument
def function_with_mutable_default(items: builtins.list[str] = []) -> builtins.list[str]:
    """Function with mutable default argument - VIOLATION."""
    items.append("new_item")
    return items


# VIOLATION Key 26: Another mutable default (dict)
def function_with_dict_default(config: builtins.dict[str, Any] = {}) -> builtins.dict[str, Any]:
    """Function with dict default argument - VIOLATION."""
    config["key"] = "value"
    return config


# VIOLATION Key 26: Set default
def function_with_set_default(seen: set = set()) -> set:
    """Function with set default argument - VIOLATION."""
    seen.add("item")
    return seen


# VIOLATION Key 34: None comparison with ==
def check_none_wrong(value: Any) -> bool:
    """Uses == for None comparison instead of 'is'."""
    if value == None:  # VIOLATION
        return True
    return False


# VIOLATION Key 34: None comparison with !=
def check_not_none_wrong(value: Any) -> bool:
    """Uses != for None comparison instead of 'is not'."""
    if value != None:  # VIOLATION
        return False
    return True


# VIOLATION Key 33: Float equality comparison
def compare_floats(a: float, b: float) -> bool:
    """Direct float equality comparison - VIOLATION."""
    return a == 0.1  # VIOLATION - should use math.isclose()


# VIOLATION Key 36: Shadowed builtin (function name)
def list() -> builtins.list[Any]:
    """Function name shadows builtin 'list' - VIOLATION."""
    return []


# VIOLATION Key 36: Shadowed builtin (class name)
class dict:
    """Class name shadows builtin 'dict' - VIOLATION."""

    pass


# VIOLATION Key 29: Assert in production code
def validate_input(x: int) -> int:
    """Uses assert in production code - VIOLATION."""
    assert x > 0, "x must be positive"  # VIOLATION
    return x


# Summary of violations in this file:
# - Key 26: 3 mutable default arguments (lines 15, 22, 29)
# - Key 34: 2 None comparisons with == or != (lines 36, 44)
# - Key 33: 1 float equality comparison (line 52)
# - Key 36: 2 shadowed builtins (lines 57, 63)
# - Key 29: 1 assert in production (line 70)