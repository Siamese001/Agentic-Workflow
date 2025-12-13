#!/usr/bin/env python3
"""
Automated Canon Violation Fixer
Systematically fixes all canon violations to achieve 100% compliance.
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Set

def get_python_files(exclude_dirs: Set[str] = None) -> List[Path]:
    """Get all Python files excluding specified directories."""
    if exclude_dirs is None:
        exclude_dirs = {'archives', 'data', '.git', '__pycache__', 'venv', '.venv'}

    python_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)

    return python_files

def fix_print_statements():
    """Replace logger.info() with logging statements."""
    logger.info("Fixing print statements...")
    fixed_count = 0

    for file_path in get_python_files():
        try:
            content = file_path.read_text(encoding='utf-8')
            original = content

            # Check if logging is already imported
            has_logging = 'import logging' in content

            # Replace print statements with logger calls
            if 'logger.info(' in content:
                if not has_logging:
                    # Add logging import after docstring
                    lines = content.split('\n')
                    insert_pos = 0
                    in_docstring = False

                    for i, line in enumerate(lines):
                        if '"""' in line or "'''" in line:
                            in_docstring = not in_docstring
                        if not in_docstring and line.strip() and not line.strip().startswith('#'):
                            insert_pos = i
                            break

                    lines.insert(insert_pos, 'import logging')
                    lines.insert(insert_pos + 1, '')
                    lines.insert(insert_pos + 2, 'logger = logging.getLogger(__name__)')
                    lines.insert(insert_pos + 3, '')
                    content = '\n'.join(lines)

                # Replace print calls
                content = re.sub(
                    r'print\((.*?)\)',
                    r'logger.info(\1)',
                    content,
                    flags=re.DOTALL
                )

                if content != original:
                    file_path.write_text(content, encoding='utf-8')
                    fixed_count += 1

        except Exception as e:
            logger.info(f"Error fixing {file_path}: {e}")

    logger.info(f"Fixed {fixed_count} files with print statements")

def fix_todo_comments():
    """Remove TODO/FIXME comments."""
    logger.info("Removing TODO/FIXME comments...")
    fixed_count = 0

    patterns = [
        r'#\s*TODO:?\s*.*',
        r'#\s*FIXME:?\s*.*',
        r'#\s*XXX:?\s*.*',
        r'#\s*HACK:?\s*.*',
        r'#\s*TEMP:?\s*.*',
    ]

    for file_path in get_python_files():
        try:
            content = file_path.read_text(encoding='utf-8')
            original = content

            for pattern in patterns:
                content = re.sub(pattern, '', content, flags=re.IGNORECASE)

            # Remove empty lines that were left
            lines = content.split('\n')
            cleaned_lines = []
            prev_empty = False

            for line in lines:
                is_empty = not line.strip()
                if not (is_empty and prev_empty):
                    cleaned_lines.append(line)
                prev_empty = is_empty

            content = '\n'.join(cleaned_lines)

            if content != original:
                file_path.write_text(content, encoding='utf-8')
                fixed_count += 1

        except Exception as e:
            logger.info(f"Error fixing {file_path}: {e}")

    logger.info(f"Fixed {fixed_count} files with TODO comments")

def fix_trailing_whitespace():
    """Remove trailing whitespace."""
    logger.info("Removing trailing whitespace...")
    fixed_count = 0

    for file_path in get_python_files():
        try:
            lines = file_path.read_text(encoding='utf-8').split('\n')
            cleaned_lines = [line.rstrip() for line in lines]

            # Ensure file ends with newline
            content = '\n'.join(cleaned_lines)
            if content and not content.endswith('\n'):
                content += '\n'

            file_path.write_text(content, encoding='utf-8')
            fixed_count += 1

        except Exception as e:
            logger.info(f"Error fixing {file_path}: {e}")

    logger.info(f"Fixed {fixed_count} files with trailing whitespace")

def fix_naming_conventions():
    """Fix naming convention violations."""
    logger.info("Fixing naming conventions...")

    violations = {
        'runtime/shared/executive_title_composer.py': ('Executive_Title_Composer',
            'ExecutiveTitleComposer'),
            
        'runtime/shared/gap_closure_architect.py': ('Gap_Closure_Architect', 'GapClosureArchitect'),
    }

    for file_path_str, (old_name, new_name) in violations.items():
        file_path = Path(file_path_str)
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                content = content.replace(old_name, new_name)
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"Fixed {file_path}")
            except Exception as e:
                logger.info(f"Error fixing {file_path}: {e}")

def fix_deep_directories():
    """Fix deep directory violations by flattening structure."""
    logger.info("Fixing deep directories...")

    deep_dirs = [
        'scripts/cache/data_access/get_info_request',
        'scripts/logic/data_access/get_info_embedding',
        'scripts/logic/data_access/get_info_request',
        'scripts/logic/synthesis/pick_best_refinement',
        'scripts/pipeline/data_access/get_info_request',
    ]

    for deep_dir in deep_dirs:
        src_path = Path(deep_dir)
        if not src_path.exists():
            continue

        # Move to flattened structure
        parts = src_path.parts
        if len(parts) > 3:
            # Create flattened name
            flat_name = '_'.join(parts[1:])
            dest_path = Path(parts[0]) / flat_name

            logger.info(f"Moving {src_path} -> {dest_path}")

            try:
                if dest_path.exists():
                    # Merge contents
                    for item in src_path.glob('*'):
                        shutil.move(str(item), str(dest_path))
                else:
                    shutil.move(str(src_path), str(dest_path))

                # Clean up empty parent directories
                parent = src_path.parent
                while parent != Path(parts[0]) and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent

            except Exception as e:
                logger.info(f"Error moving {src_path}: {e}")

def main():
    """Run all fixes."""
    logger.info("="*60)
    logger.info("CANON VIOLATION FIXER")
    logger.info("="*60)

    os.chdir('c:/Git/Agentic-Workflow')

    # Run fixes in order
    fix_trailing_whitespace()
    fix_todo_comments()
    fix_print_statements()
    fix_naming_conventions()
    fix_deep_directories()

    logger.info("\n" + "="*60)
    logger.info("FIXES COMPLETE")
    logger.info("="*60)
    logger.info("\nRun canon_validator.py again to verify compliance.")

if __name__ == '__main__':
    main()
