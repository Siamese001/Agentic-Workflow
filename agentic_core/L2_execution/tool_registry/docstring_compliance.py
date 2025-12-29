# DocstringComplianceAgent - Atomic Validator (Ungated Healing)
# Territory: agentic_core/L2_execution/tool_registry
# Canon Alignment: Enforces self-documenting code via mandatory docstrings (hygiene/signal)
# Surgery Scope: Single file — adds minimal compliant docstrings where missing

import ast
from pathlib import Path
from typing import Dict, Any


class DocstringComplianceAgent:
    """
    Ensures public functions, classes, and modules have docstrings.

    Rules:
    - Module-level docstring required (first statement)
    - Public classes (not starting with _) must have docstring
    - Public functions/methods (not starting with _) must have docstring
    - Minimal stub: '''Brief description of functionality and purpose.'''

    Why ungated healing is safe:
    - Only adds missing triple-quoted strings immediately after def/class
    - Never removes or modifies existing content
    - Single-file scope
    """

    MIN_DOCSTRING = "'''Brief description of functionality and purpose.'''"

    async def heal_violation(self, file_path: Path, ctx) -> Dict[str, Any]:
        """
        Per-file healing: add missing docstrings.
        """
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)

            # Collect nodes that need docstrings
            needs_docstring = []

            # Module docstring check
            if not ast.get_docstring(tree):
                needs_docstring.append(("module", 0))

            # Classes and functions check
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name.startswith("_"):
                        continue  # Private — skip per hygiene laws
                    if ast.get_docstring(node) is None:
                        needs_docstring.append((type(node).__name__, node.lineno))

            if not needs_docstring:
                return {"healed": False}

            # Apply fixes to the lines
            lines = source.splitlines(keepends=True)
            new_lines = lines.copy()
            added_count = 0

            # Sort by line number descending to avoid index shifts during mutation
            needs_docstring.sort(key=lambda x: x[1] if x[0] != "module" else 0, reverse=True)

            for node_type, lineno in needs_docstring:
                if node_type == "module":
                    # Insert after first non-comment/shebang line
                    insert_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip() and not line.strip().startswith(('#', '__')):
                            insert_idx = i + 1
                            break
                    indent = ""
                else:
                    # Insert immediately after the declaration line
                    insert_idx = lineno  # 1-based lineno corresponds to lines[lineno]
                    def_line = lines[lineno - 1]
                    indent = "    " * (len(def_line) - len(def_line.lstrip()) + 1)

                doc_lines = [f"{indent}{self.MIN_DOCSTRING}\n", f"{indent}\n"]
                new_lines[insert_idx:insert_idx] = doc_lines
                added_count += 1

            if added_count > 0:
                new_content = "".join(new_lines)
                file_path.write_text(new_content, encoding="utf-8")
                message = f"Added {added_count} missing docstring(s)"
                print(f"      [HEALED] {file_path.name}: {message}")
                ctx.report(
                    self.__class__.__name__,
                    key_id=18,  # Core Laws / Hygiene category
                    success=True,
                    msg=message,
                )
                return {"healed": True, "details": message}

            return {"healed": False}

        except Exception as e:
            ctx.report(
                self.__class__.__name__,
                18,
                False,
                f"Docstring healing failed: {str(e)[:100]}",
            )
            return {"healed": False}


# Factory for dynamic discovery
def get_docstring_compliance_agent():
    return DocstringComplianceAgent()
