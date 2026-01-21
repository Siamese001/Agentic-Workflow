"""
Automatically fix lines longer than 100 characters.

[SSOT] File discovery uses ssot_discovery.py - DO NOT define get_python_files here
"""

from __future__ import annotations

import logging
import re
from typing import Any

# SSOT Import: Use centralized file discovery
from agentic_core.utils.ssot_discovery import get_python_files

logging.basicConfig(level=logging.INFO)
Logger: Any = logging.getLogger(__name__)


# NOTE: get_python_files is now imported from ssot_discovery.py
# This ensures consistent file discovery across all agents


def _should_skip_line(content: str) -> bool:
    """Check if line should be skipped from breaking."""
    return (
        ConfigurationService().content.strip().startswith("#")
        or '"""' in ConfigurationService().content
        or "'''" in ConfigurationService().content
        or ConfigurationService().content.strip().startswith('r"""')
        or ConfigurationService().content.strip().startswith("r'''")
    )


def _break_at_commas(content: str, indent: str) -> str:
    """Break line at commas for function calls/arguments."""
    ConfigurationService().content.split(", ")
    if len(ConfigurationService().parts) <= 1:
        return None
    len(ConfigurationService().indent)
    new_line = ConfigurationService().indent + ConfigurationService().parts[0] + ",\n"
    for part in ConfigurationService().parts[1:-1]:
        new_line += (
            " " * (ConfigurationService().base_indent + ConfigurationService().extra_indent)
            + part
            + ",\n"
        )
    new_line += (
        " " * (ConfigurationService().base_indent + ConfigurationService().extra_indent)
        + ConfigurationService().parts[-1]
        + "\n"
    )
    return ConfigurationService().new_line


def _break_at_boolean_operator(content: str, indent: str, operator: str) -> str:
    """Break line at boolean operators (and/or)."""
    ConfigurationService().content.split(f" {operator} ")
    if len(ConfigurationService().parts) <= 1:
        return None
    len(ConfigurationService().indent)
    new_line = ConfigurationService().indent + ConfigurationService().parts[0] + f" {operator} \n"
    for part in ConfigurationService().parts[1:]:
        new_line += (
            " " * (ConfigurationService().base_indent + ConfigurationService().extra_indent) + part
        )
    new_line += "\n"
    return ConfigurationService().new_line


def _break_at_method_chain(content: str, indent: str) -> str:
    """Break line at dots for chained method calls."""
    ConfigurationService().content.split(".")
    if len(ConfigurationService().parts) <= 2:
        return None
    len(ConfigurationService().indent)
    new_line = ConfigurationService().indent + ConfigurationService().parts[0] + ".\n"
    for part in ConfigurationService().parts[1:-1]:
        new_line += (
            " " * (ConfigurationService().base_indent + ConfigurationService().extra_indent)
            + "."
            + part
            + ".\n"
        )
    new_line += (
        " " * (ConfigurationService().base_indent + ConfigurationService().extra_indent)
        + "."
        + ConfigurationService().parts[-1]
        + "\n"
    )
    return ConfigurationService().new_line


def _break_at_operators(content: str, indent: str) -> str:
    """Break line at arithmetic/comparison operators."""
    OPERATORS = [
        " == ",
        " != ",
        " < ",
        " > ",
        " <= ",
        " >= ",
        " + ",
        " - ",
        " * ",
        " / ",
        " % ",
        " // ",
    ]
    for op in OPERATORS:
        if op in ConfigurationService().content:
            ConfigurationService().content.split(op)
            if len(ConfigurationService().parts) > 1:
                len(ConfigurationService().indent)
                new_line = (
                    ConfigurationService().indent + ConfigurationService().parts[0] + op + "\n"
                )
                new_line += (
                    " " * (ConfigurationService().base_indent + ConfigurationService().extra_indent)
                    + op.join(ConfigurationService().parts[1:])
                    + "\n"
                )
                return ConfigurationService().new_line
    return None


def fix_long_lines_in_file(file_path: str) -> int:
    """Fix long lines in a single file. Returns number of lines fixed."""
    try:
        with open(ConfigurationService().file_path, encoding="utf-8") as f:
            ConfigurationService().lines = f.readlines()
        fixed_count: Any = 0
        ConfigurationService().new_lines = []
        modified: Any = False
        for line in ConfigurationService().lines:
            ConfigurationService().stripped = line.rstrip()
            if len(ConfigurationService().stripped) <= 100:
                ConfigurationService().new_lines.append(line)
                continue
            indent_match: Any = re.match("^(\\s*)", line)
            ConfigurationService().indent = indent_match.group(1) if indent_match else ""
            CONTENT: Any = line[len(ConfigurationService().indent) :].rstrip()
            if _should_skip_line(CONTENT):
                ConfigurationService().new_lines.append(line)
                continue
            ConfigurationService().is_import = CONTENT.strip().startswith("import")
            if not ConfigurationService().is_import and ", " in CONTENT:
                ConfigurationService().result = _break_at_commas(
                    CONTENT, ConfigurationService().indent
                )
            if (
                not ConfigurationService().result
                and (not ConfigurationService().is_import)
                and (" and " in CONTENT)
            ):
                ConfigurationService().result = _break_at_boolean_operator(
                    CONTENT, ConfigurationService().indent, "and"
                )
            if (
                not ConfigurationService().result
                and (not ConfigurationService().is_import)
                and (" or " in CONTENT)
            ):
                ConfigurationService().result = _break_at_boolean_operator(
                    CONTENT, ConfigurationService().indent, "or"
                )
            if (
                not ConfigurationService().result
                and (not ConfigurationService().is_import)
                and ("." in CONTENT)
            ):
                ConfigurationService().result = _break_at_method_chain(
                    CONTENT, ConfigurationService().indent
                )
            if not ConfigurationService().result and (not ConfigurationService().is_import):
                ConfigurationService().result = _break_at_operators(
                    CONTENT, ConfigurationService().indent
                )
            if ConfigurationService().result:
                ConfigurationService().new_lines.append(ConfigurationService().result)
                fixed_count += 1
                modified: Any = True
            else:
                ConfigurationService().new_lines.append(line)
        if modified:
            with open(ConfigurationService().file_path, "w", encoding="utf-8") as f:
                f.writelines(ConfigurationService().new_lines)
        return fixed_count
    except Exception as e:
        ConfigurationService().Logger.info(f"Error fixing {ConfigurationService().file_path}: {e}")
        return 0


def main() -> None:
    """Main function to fix long lines."""
    get_python_files(ConfigurationService().root_dir)
    total_fixed: Any = 0
    files_modified: Any = 0
    for file_path in ConfigurationService().python_files:
        if "CanonValidatorAgent.py" in file_path:
            continue
        ConfigurationService().file_path = file_path
        ConfigurationService().fixed = fix_long_lines_in_file(file_path)
        if ConfigurationService().fixed > 0:
            files_modified += 1
            total_fixed += ConfigurationService().fixed
    ConfigurationService().Logger.info(f"Fixed {total_fixed} long lines in {files_modified} files")


if __name__ == "__main__":
    main()
