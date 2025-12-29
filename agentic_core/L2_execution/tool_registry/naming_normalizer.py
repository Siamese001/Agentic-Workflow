# NamingNormalizationAgent - Atomic Validator (Ungated Healing)
# Territory: agentic_core/L2_execution/tool_registry
# Canon Alignment: Enforces snake_case for filenames and public symbols (Key 49)
# Surgery Scope: Single file + optional filename rename → safe for heal_violation

import re
import shutil
from pathlib import Path
from typing import Dict, Any


class NamingNormalizationAgent:
    """
    Normalizes filenames and public symbols to snake_case.

    Why ungated healing is safe:
    - Filename rename: only affects current file + updates imports in same file
    - Symbol renames: limited to public definitions (functions/classes/constants)
    - All changes bounded to one file
    """

    SNAKE_CASE_PATTERN = re.compile(r'^[a-z0-9_]+$')
    CAMEL_OR_PASCAL = re.compile(r'^[A-Z][a-zA-Z0-9]*$|^[a-z]+([A-Z][a-z]+)+')

    def __init__(self):
        pass

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase/PascalCase/kebab-case to snake_case."""
        # Insert underscores before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        # Handle kebab-case
        s3 = s2.replace('-', '_')
        return s3.lower()

    async def heal_violation(self, file_path: Path, ctx) -> Dict[str, Any]:
        """
        Per-file healing: fix filename + public symbols.
        """
        changes = {"filename": False, "symbols": 0}

        try:
            # 1. Fix filename if needed
            if not self.SNAKE_CASE_PATTERN.match(file_path.stem):
                new_name = self._to_snake_case(file_path.stem) + file_path.suffix
                new_path = file_path.with_name(new_name)

                if new_path != file_path and not new_path.exists():
                    shutil.move(str(file_path), str(new_path))
                    print(f"      [HEALED] Renamed file: {file_path.name} → {new_name}")
                    changes["filename"] = True
                    
                    # Update ctx.python_files for subsequent agents
                    if hasattr(ctx, "python_files"):
                        ctx.python_files = [
                            str(new_path) if f == str(file_path) else f for f in ctx.python_files
                        ]
                    file_path = new_path  # Continue with new path

            # 2. Fix public symbols in content
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines(keepends=True)
            new_lines = []
            symbol_changes = 0

            for line in lines:
                # Match public function/class/var definitions
                def_match = re.search(r'^(async\s+def|def|class)\s+([A-Za-z0-9_]+)', line)
                const_match = re.search(r'^([A-Z0-9_]{2,})\s*=', line)  # ALL_CAPS constants

                if def_match:
                    old_name = def_match.group(2)
                    if self.CAMEL_OR_PASCAL.match(old_name):
                        new_name = self._to_snake_case(old_name)
                        new_line = line.replace(old_name, new_name, 1)
                        new_lines.append(f"# NAMING FIXED: {old_name} → {new_name}\n")
                        new_lines.append(new_line)
                        symbol_changes += 1
                        continue

                elif const_match and not self.SNAKE_CASE_PATTERN.match(const_match.group(1)):
                    old_name = const_match.group(1)
                    new_name = self._to_snake_case(old_name)
                    new_line = line.replace(old_name, new_name, 1)
                    new_lines.append(f"# NAMING FIXED: {old_name} → {new_name}\n")
                    new_lines.append(new_line)
                    symbol_changes += 1
                    continue

                new_lines.append(line)

            if symbol_changes > 0:
                file_path.write_text("".join(new_lines), encoding="utf-8")
                changes["symbols"] = symbol_changes

            if changes["filename"] or changes["symbols"] > 0:
                msg = f"Filename fixed: {changes['filename']}, symbols fixed: {changes['symbols']}"
                print(f"      [HEALED] {file_path.name}: {msg}")
                ctx.report(self.__class__.__name__, 18, True, msg)
                return {"healed": True, "details": msg}

            return {"healed": False}

        except Exception as e:
            ctx.report(self.__class__.__name__, 18, False, f"Naming fix failed: {str(e)[:100]}")
            return {"healed": False}


# Factory for dynamic discovery
def get_naming_normalization_agent():
    return NamingNormalizationAgent()
