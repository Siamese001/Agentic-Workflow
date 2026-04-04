"""
ADG Exception Classification Module

AST-based bare except detection for hardened validation.
Implements the specification from ADG FALSE POSITIVE HARDENING document.

Key features:
- AST-based classification (ground truth)
- Zero false positives for exception tuples
n- Correct evidence strings: except:bare, except:broad, except:valid
"""

import ast


def classify_except_handler(node: ast.ExceptHandler) -> str | None:
    """
    Classify an exception handler using AST analysis.

    Returns:
        - "except:bare"    → for bare `except:` (type=None)
        - "except:broad"   → for `except Exception:`
        - None             → for valid specific or tuple exceptions

    This is the authoritative classification per ADG hardening spec.
    """
    if node.type is None:
        # Bare except: except:
        return "except:bare"

    elif isinstance(node.type, ast.Tuple):
        # Exception tuple: except (Error1, Error2):
        # These are VALID - not violations
        return None

    elif isinstance(node.type, ast.Name):
        # Specific exception: except SomeError:
        if node.type.id == "Exception":
            # Broad exception catch
            return "except:broad"
        # Specific exception (ImportError, ValueError, etc.)
        return None

    elif isinstance(node.type, ast.Attribute):
        # Module exception: except os.error:
        # Check if base is Exception
        if isinstance(node.type.value, ast.Name) and node.type.value.id == "Exception":
            return "except:broad"
        return None

    else:
        # Unknown pattern - don't flag (fail safe)
        return None


def scan_file_for_exceptions(filepath: str) -> list[tuple[int, str, str]]:
    """
    Scan a Python file for exception handler violations.

    Returns list of (line_no, classification, source_line) tuples.
    Only returns actual violations (bare or broad), not valid tuples.
    """
    violations = []

    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            source = f.read()
            lines = source.splitlines()
    except Exception:
        return violations

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return violations

    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            classification = classify_except_handler(node)
            if classification:  # Only record violations
                # Get the source line
                line_idx = node.lineno - 1
                if 0 <= line_idx < len(lines):
                    source_line = lines[line_idx].strip()
                else:
                    source_line = ""
                violations.append((node.lineno, classification, source_line))

    return violations


# Regression test cases per hardening spec
TEST_CASES = [
    ("except:", "except:bare"),
    ("except Exception:", "except:broad"),
    ("except (OSError, IOError):", None),  # VALID - not violation
    ("except (ValueError, TypeError) as e:", None),  # VALID
    ("except ImportError:", None),  # VALID
    ("except ValueError:", None),  # VALID
    ("except os.error:", None),  # VALID
]


def run_regression_tests() -> bool:
    """
    Run regression tests for exception classification.

    Returns True if all tests pass, False otherwise.
    """
    all_passed = True

    for code, expected in TEST_CASES:
        try:
            # Wrap in try/except structure for AST parsing
            wrapped = f"try:\n    pass\n{code}\n    pass"
            tree = ast.parse(wrapped)

            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    result = classify_except_handler(node)
                    if result == expected:
                        print(f"✓ PASS: {code!r} -> {result}")
                    else:
                        print(f"✗ FAIL: {code!r} -> {result} (expected: {expected})")
                        all_passed = False
                    break
        except Exception as e:
            print(f"✗ ERROR: {code!r} -> {e}")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("Running ADG Exception Classification Regression Tests")
    print("=" * 60)
    success = run_regression_tests()
    print("=" * 60)
    if success:
        print("All tests PASSED ✓")
    else:
        print("Some tests FAILED ✗")
        exit(1)
