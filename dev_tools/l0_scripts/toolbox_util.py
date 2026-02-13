from __future__ import annotations

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import logging
import os
from typing import Any

Logger: Any = logging.getLogger("Toolbox")


def repository_get_file_content(file_path: Any) -> Any:
    """Safely reads a file from the repository."""
    try:
        # guardian: allow-path-string
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist."
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    # guardian: allow-silent-swallow
    except Exception as e:
        return f"Error reading file: {e}"


def repository_list_files(directory: Any = ".") -> Any:
    """Lists python files in the directory recursively."""
    try:
        if ".." in directory:
            return "Error: Cannot navigate up the directory tree."
        # Phase 6.8: Use ssot_discovery instead of glob
        from pathlib import Path

        from agentic_core.utils.ssot_discovery_validator import get_python_files

        return [str(f) for f in get_python_files(Path(directory))]
    # guardian: allow-silent-swallow
    except Exception as e:
        return f"Error listing files: {e}"


def repository_save_file(file_path: Any, content: Any) -> Any:
    """Safely writes content to a file. Creates directories if needed."""
    try:
        if ".git" in file_path or ".env" in file_path:
            return f"Error: Write access denied for sensitive file '{file_path}'."
        # guardian: allow-path-string
        directory: Any = os.path.dirname(file_path)
        # guardian: allow-path-string
        if directory and (not os.path.exists(directory)):
            os.makedirs(directory, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Success: File '{file_path}' saved."
    # guardian: allow-silent-swallow
    except Exception as e:
        return f"Error writing file: {e}"


safe_tools: Any = {
    "repository_get_file_content": repository_get_file_content,
    "repository_list_files": repository_list_files,
    "repository_save_file": repository_save_file,
    "write_file": repository_save_file,
    "print": print,
    "len": len,
    "os": os,
}
toolbox_desc: Any = '\nYou have access to the following file system tools. DO NOT hallucinate other tools.\n1. `repository_list_files(directory=".")`: List all Python files.\n2. `repository_get_file_content(file_path)`: Read the content of a specific file.\n3. `repository_save_file(file_path, content)`: Write code to a file. Will create directories if needed.\n4. `write_file(file_path, content)`: Alias for repository_save_file.\n\nTo use them, simply write the Python code calling these functions.\nIMPORTANT: These are real functions available in your execution context.\nExample: write_file("filename.py", "content")\n'
