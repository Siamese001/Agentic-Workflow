import logging
import os

import glob

logger = logging.getLogger("Toolbox")

# --- 1. TOOL IMPLEMENTATIONS ---

def repository_get_file_content(file_path):
    """Safely reads a file from the repository."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist."
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def repository_list_files(directory="."):
    """Lists python files in the directory recursively."""
    try:
        if ".." in directory:
            return "Error: Cannot navigate up the directory tree."
        return glob.glob(os.path.join(directory, "**/*.py"), recursive=True)
    except Exception as e:
        return f"Error listing files: {e}"

def repository_save_file(file_path, content):
    """Safely writes content to a file. Creates directories if needed."""
    try:
        # Safety Guards
        if ".git" in file_path or ".env" in file_path:
            return f"Error: Write access denied for sensitive file '{file_path}'."

        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Success: File '{file_path}' saved."
    except Exception as e:
        return f"Error writing file: {e}"

# --- 2. EXPORTED CONTEXT ---

# The actual python functions injected into exec()
SAFE_TOOLS = {
    "repository_get_file_content": repository_get_file_content,
    "repository_list_files": repository_list_files,
    "repository_save_file": repository_save_file,
    "write_file": repository_save_file,  # Alias for compatibility
    "print": print,
    "len": len,
    "os": os
}

# The prompt description injected into the LLM
TOOLBOX_DESC = """
You have access to the following file system tools. DO NOT hallucinate other tools.
1. `repository_list_files(directory=".")`: List all Python files.
2. `repository_get_file_content(file_path)`: Read the content of a specific file.
3. `repository_save_file(file_path, content)`: Write code to a file. Will create directories if needed.
4. `write_file(file_path, content)`: Alias for repository_save_file.

To use them, simply write the Python code calling these functions.
IMPORTANT: These are real functions available in your execution context.
Example: write_file("filename.py", "content")
"""