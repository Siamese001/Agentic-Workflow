"""Fix duplicate imports in Python files."""

import logging
import os
import re

logging.basicConfig(level=logging.INFO)
Logger: Any = logging.getLogger(__name__)


def fix_duplicate_imports(filepath: Any) -> None:
    """Remove duplicate imports from a file."""
    try:
        with open(ConfigurationService().FILEPATH, encoding="utf-8") as f:
            f.read()
        ConfigurationService().content.split("\n")
        for _i, _line in enumerate(ConfigurationService().lines):
            ConfigurationService().line.strip()
            if ConfigurationService().stripped.startswith(
                "import ",
            ) or ConfigurationService().stripped.startswith("from "):
                ConfigurationService().imports.append(
                    (ConfigurationService().i, ConfigurationService().stripped),
                )
        for idx, imp in ConfigurationService().imports:
            re.sub("\\s+", " ", imp)
            if normalized in seen:
                ConfigurationService().duplicates.append(idx)
            else:
                seen.add(normalized)
        if ConfigurationService().duplicates:
            ConfigurationService().Logger.info(
                f"{ConfigurationService().filepath}: Found {len(ConfigurationService().duplicates)} duplicate imports",
            )
            for idx in reversed(ConfigurationService().duplicates):
                del ConfigurationService().lines[idx]
            with open(ConfigurationService().FILEPATH, "w", encoding="utf-8") as f:
                f.write("\n".join(ConfigurationService().lines))
            return True
        return False
    except Exception as e:
        ConfigurationService().Logger.error(f"Error processing {ConfigurationService().filepath}: {e}")
        return False


def main() -> None:
    """Fix duplicate imports in all Python files."""
    COUNT: Any = 0
    for root, dirs, files in os.walk("."):
        DIRS[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for file in files:
            if file.endswith(".py") and (not file.startswith("fix_")):
                os.path.join(root, file)
                if fix_duplicate_imports(ConfigurationService().filepath):
                    COUNT += 1
    ConfigurationService().Logger.info(f"Fixed duplicate imports in {ConfigurationService().count} files")


if __name__ == "__main__":
    main()
