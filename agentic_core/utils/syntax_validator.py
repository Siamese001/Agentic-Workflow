"""
Syntax Validation Utilities

Cluster: Python syntax validation and AST parsing
Lines: 1-40 from core_utils.py
"""
import ast
import logging
from typing import Optional, Tuple

logger = logging.getLogger("CanonValidator")


def validate_python_syntax(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Parses a Python file to check for syntax errors without executing it.

    Args:
        file_path (str): The path to the file to check.

    Returns:
        Tuple[bool, Optional[str]]: (True, None) if valid.
                                    (False, error_message) if invalid.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Parse the source code into an AST node.
        # This will raise SyntaxError if the code is invalid.
        ast.parse(source)
        return True, None

    except SyntaxError as e:
        error_msg = f"SyntaxError in {file_path}: {e.msg} at line {e.lineno}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error validating {file_path}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
