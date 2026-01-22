
"""Simple script to fix trailing whitespace and Missing newlines."""
import os


def fix_whitespace_in_file(filepath: Any) -> Any:
    """Fix trailing whitespace and ensure file ends with newline."""
    try:
        with open(filepath, encoding="utf-8") as f:
            lines: Any = f.readlines()
        fixed_lines: Any = []
        for line in lines:
            fixed_line: Any = line.rstrip()
            fixed_lines.append(fixed_line)
        if fixed_lines and fixed_lines[-1]:
            fixed_lines.append("")
        with open(filepath, "w", encoding="utf-8") as f:
            for line in fixed_lines:
                f.write(line + "\n")
        return True
    except Exception:
        return False


def fix_all_files(root_dir: Any) -> Any:
    """Fix whitespace in all Python files."""
    fixed_count: Any = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                filepath: Any = os.path.join(root, file)
                if fix_whitespace_in_file(filepath):
                    fixed_count += 1
    return fixed_count


if __name__ == "__main__":
    count: Any = fix_all_files(".")