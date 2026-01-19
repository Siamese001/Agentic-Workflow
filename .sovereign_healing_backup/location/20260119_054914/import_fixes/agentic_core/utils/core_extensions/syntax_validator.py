from __future__ import annotations
import ast
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import logging
from typing import Any, Dict, List, Optional, Protocol, Tuple
from agentic_core.utils.file_utils import safe_read_file, safe_write_file
Logger: Any = logging.getLogger('CanonValidator')

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
            source: Any = f.read()
        ast.parse(source)
        return (True, None)
    except SyntaxError as e:
        error_msg: Any = f'SyntaxError in {file_path}: {e.msg} at line {e.lineno}'
        Logger.error(error_msg)
        return (False, error_msg)
    except Exception as e:
        error_msg: Any = f'Unexpected error validating {file_path}: {str(e)}'
        Logger.error(error_msg)
        return (False, error_msg)
