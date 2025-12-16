import os
import re
import sys
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# TARGET DIRECTORY: Current directory (or /app inside docker)
ROOT_DIR = "."

# SKIP LIST (Don't break git or cache)
SKIP_DIRS = {'.git', '__pycache__', '.mypy_cache',
             'venv', 'env', 'reports', 'drafts'}


def fix_bare_except(lines, i, line, new_lines, modified):
    """
    Identifies and fixes bare except blocks by replacing them with
    'except Exception as e:' and adding a comment.
    """
    # Matches "except:" followed by newline or comment
    if re.match(r'^\s*except\s*:', line) or re.match(r'^\s*except\s*#', line):
        # Preserve indentation
        indent = line[:len(line) - len(line.lstrip())]
        new_line = f"{indent}except Exception as e:  # Fixed by Gemini Force-Fix\n"
        new_lines.append(new_line)
        logging.info(f"  [Fixed Bare Except] Line {i + 1}")
        modified = True
    else:
        new_lines.append(line)
    return modified


def flag_star_imports(lines, i, line, new_lines):
    """
    Flags star imports, as they cannot be safely auto-fixed without
    manual review.
    """
    if re.match(r'^from .* import \*', line):
        logging.warning(
            f"  [WARNING: Star Import] Line {i + 1}: {line.strip()} (Requires Manual Review)")
        # OPTIONAL: Uncomment to disable them temporarily to force explicit import errors
        # new_lines.append(f"# {line}")
        new_lines.append(line)
    else:
        new_lines.append(line)


def process_file(filepath):
    """
    Reads a Python file, applies hygiene fixes, and writes back if modified.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        logging.error(f"❌ Failed to read {filepath}: {e}")
        return

    new_lines = []
    modified = False

    for i, line in enumerate(lines):
        # 1. FIX BARE EXCEPTS (Key 1 & 2)
        modified = fix_bare_except(lines, i, line, new_lines, modified)

        # 2. FLAGGING STAR IMPORTS (Key 7)
        # We can't auto-fix safely without knowing what's used,
        # but we can replace common ones if we know them.
        if not re.match(r'^\s*except', line) and not re.match(r'^\s*except\s*#', line):  # Avoid double processing
            flag_star_imports(lines, i, line, new_lines)


    if modified:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            logging.info(f"✅ Saved changes to {filepath}")
        except Exception as e:
            logging.error(f"❌ Failed to save changes to {filepath}: {e}")


def main():
    logging.info(f"🚀 Starting Surgical Hygiene Fix on {os.path.abspath(ROOT_DIR)}")
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                process_file(filepath)


if __name__ == "__main__":
    main()

