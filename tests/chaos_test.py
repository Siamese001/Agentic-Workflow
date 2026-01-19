"""
chaos_test.py - Comprehensive AST Violation Test File

This file intentionally contains EVERY type of violation that the
UnifiedASTValidatorAgent should detect. Used for:
1. AST Visitor Coverage testing
2. Parallel execution validation (shadow mode)
3. Regression testing after consolidation

Expected violations:
- Key 3: Debugger statements (breakpoint, pdb.set_trace) - 3 instances
- Key 4: Empty except blocks - 3 instances (includes bare except with pass)
- Key 5: Bare except statements - 2 instances
- Key 6: eval/exec calls - 4 instances (includes eval inside function_with_bare_except)
- Key 42: Dangerous builtins - 5 instances

Total expected violations: 17
"""
from __future__ import annotations

import pdb


# =============================================================================
# KEY 3: DEBUGGER STATEMENTS (3 violations expected)
# =============================================================================

def function_with_breakpoint():
    """Contains breakpoint() - should be detected."""
    x = 1
    breakpoint()  # VIOLATION: Key 3 - debugger breakpoint
    return x


def function_with_pdb_set_trace():
    """Contains pdb.set_trace() - should be detected."""
    y = 2
    pdb.set_trace()  # VIOLATION: Key 3 - pdb.set_trace
    return y


def another_breakpoint_usage():
    """Another breakpoint for coverage."""
    breakpoint()  # VIOLATION: Key 3 - debugger breakpoint
    pass


# =============================================================================
# KEY 4: EMPTY EXCEPT BLOCKS (2 violations expected)
# =============================================================================

def function_with_empty_except():
    """Contains empty except block - should be detected."""
    try:
        risky_operation = 1 / 0
    except ZeroDivisionError:
        pass  # VIOLATION: Key 4 - empty except block


def another_empty_except():
    """Another empty except for coverage."""
    try:
        x = int("not a number")
    except ValueError:
        pass  # VIOLATION: Key 4 - empty except block


# =============================================================================
# KEY 5: BARE EXCEPT STATEMENTS (2 violations expected)
# =============================================================================

def function_with_bare_except():
    """Contains bare except - should be detected."""
    try:
        dangerous_call = eval("1+1")
    except:  # VIOLATION: Key 5 - bare except (no exception type)
        print("Caught something")


def another_bare_except():
    """Another bare except for coverage."""
    try:
        x = 1 / 0
    except:  # VIOLATION: Key 5 - bare except
        pass  # Also Key 4 violation (empty)


# =============================================================================
# KEY 6: EVAL/EXEC CALLS (3 violations expected)
# =============================================================================

def function_with_eval():
    """Contains eval() - should be detected."""
    result = eval("2 + 2")  # VIOLATION: Key 6 - forbidden eval()
    return result


def function_with_exec():
    """Contains exec() - should be detected."""
    exec("x = 42")  # VIOLATION: Key 6 - forbidden exec()


def dynamic_code_execution():
    """Another eval for coverage."""
    code = "print('hello')"
    eval(code)  # VIOLATION: Key 6 - forbidden eval()


# =============================================================================
# KEY 42: DANGEROUS BUILTINS (5 violations expected)
# =============================================================================

def function_with_globals():
    """Contains globals() - should be detected."""
    g = globals()  # VIOLATION: Key 42 - dangerous builtin globals()
    return g


def function_with_locals():
    """Contains locals() - should be detected."""
    l = locals()  # VIOLATION: Key 42 - dangerous builtin locals()
    return l


def function_with_compile():
    """Contains compile() - should be detected."""
    code = compile("x = 1", "<string>", "exec")  # VIOLATION: Key 42 - dangerous builtin compile()
    return code


def function_with_vars():
    """Contains vars() - should be detected."""
    v = vars()  # VIOLATION: Key 42 - dangerous builtin vars()
    return v


def function_with_dunder_import():
    """Contains __import__() - should be detected."""
    os_module = __import__('os')  # VIOLATION: Key 42 - dangerous builtin __import__()
    return os_module


# =============================================================================
# CLEAN FUNCTIONS (should NOT trigger violations)
# =============================================================================

def clean_function():
    """This function has no violations."""
    try:
        x = 1 / 1
    except ZeroDivisionError as e:
        print(f"Error: {e}")  # Not empty - has actual handling
    return x


def another_clean_function():
    """Also clean - proper exception handling."""
    try:
        result = int("42")
    except ValueError as e:
        result = 0
        print(f"Conversion failed: {e}")
    return result


# =============================================================================
# TYPE_CHECKING BLOCK (should NOT trigger violations)
# =============================================================================

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # These should be IGNORED by the validator
    eval("this should be ignored")
    exec("this too")
    breakpoint()
    globals()
    locals()


# =============================================================================
# EXPECTED VIOLATION SUMMARY
# =============================================================================
"""
EXPECTED VIOLATIONS (15 total):

Key 3 - Debugger (3):
  1. Line ~32: breakpoint()
  2. Line ~39: pdb.set_trace()
  3. Line ~45: breakpoint()

Key 4 - Empty Except (2):
  1. Line ~56: except ZeroDivisionError: pass
  2. Line ~64: except ValueError: pass

Key 5 - Bare Except (2):
  1. Line ~75: except: (no type)
  2. Line ~83: except: (no type)

Key 6 - eval/exec (3):
  1. Line ~93: eval("2 + 2")
  2. Line ~99: exec("x = 42")
  3. Line ~105: eval(code)

Key 42 - Dangerous Builtins (5):
  1. Line ~114: globals()
  2. Line ~121: locals()
  3. Line ~128: compile()
  4. Line ~134: vars()
  5. Line ~140: __import__()

TYPE_CHECKING block violations should be IGNORED (5 calls inside block).
"""


if __name__ == "__main__":
    print("This file is for testing AST validators.")
    print("Run UnifiedASTValidatorAgent against this file to verify detection.")
