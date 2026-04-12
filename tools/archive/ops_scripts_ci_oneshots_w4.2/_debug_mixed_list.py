"""Debug why fixer misses mixed list cases."""

import ast
import sys

# guardian: allow-global-mutation
sys.path.insert(0, ".")
from pathlib import Path

content = Path("agentic_core/L0_routing/utils/scorched_earth_merge_util.py").read_text(encoding="utf-8")
tree = ast.parse(content)
for node in ast.walk(tree):
    if isinstance(node, ast.List):
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and elt.value == AGENTIC_CORE_DIR:
                print(f'Found "agentic_core" at line {elt.lineno}, col {elt.col_offset}')
                print(
                    f"  List elements: {[e.value if isinstance(e, ast.Constant) else type(e).__name__ for e in node.elts]}"
                )
                for parent in ast.walk(tree):
                    if hasattr(parent, "elts") and node in parent.elts:
                        print(f"  Parent is {type(parent).__name__}")
                    elif hasattr(parent, "value") and parent.value is node:
                        print(f"  Parent is {type(parent).__name__}")
                break
