"""Test guard to prevent reintroduction of removed prompt roots."""

from pathlib import Path


def test_no_nondoc_references_to_removed_prompt_roots():
    """Fail if any NON-DOC files reference removed prompt roots."""
    repo_root = Path(__file__).parent.parent.parent

    # Construct patterns from parts to avoid self-matching in docstring
    forbidden_patterns = ["data/" + "prompts/", "data/" + "prompt_libraries/"]

    violations = []

    # Walk repository files deterministically
    for file_path in repo_root.rglob("*"):
        if not file_path.is_file():
            continue

        # Skip ONLY docs and archives (including all subdirectories)
        file_path_str = str(file_path).replace("\\", "/")
        if "docs/" in file_path_str or "archives/" in file_path_str:
            continue

        # Skip __pycache__ directories
        if "__pycache__/" in file_path_str:
            continue

        # Read file content with error handling
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue

        # Check each line for forbidden patterns
        for line_num, line in enumerate(content.splitlines(), 1):
            for pattern in forbidden_patterns:
                if pattern in line:
                    # Get relative path from repo root
                    rel_path = str(file_path.relative_to(repo_root)).replace("\\", "/")
                    # Truncate line to first 200 chars for display
                    display_line = line[:200] + "..." if len(line) > 200 else line
                    violations.append(
                        {"file": rel_path, "line": line_num, "pattern": pattern, "content": display_line}
                    )

    if violations:
        error_msg = "Found references to removed prompt roots in non-doc files:\n\n"
        for violation in violations:
            error_msg += f"{violation['file']}:{violation['line']} - {violation['pattern']}\n"
            error_msg += f"  Content: {violation['content']}\n\n"

        error_msg += "These references must be removed to maintain SSOT boundary integrity."
        raise AssertionError(error_msg)
