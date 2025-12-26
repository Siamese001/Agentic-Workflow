"""
Sovereign Guard: Block Inline Pydantic Models (Final Sovereign Version)
Constitutional enforcement - all models must live in core_contracts.py
Signal-based filtering with timestamped, prefixed logging
"""
import ast
import sys
import logging
from pathlib import Path

# Logger Setup
logger = logging.getLogger("sovereign.models")
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("[MODELS] %(levelname)s %(asctime)s | %(message)s", "%H:%M:%S"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

CONTRACT_SIGNALS = ("Profile", "Config", "State", "Context", "Result", "Message", "Request", "Response")
EXEMPT = {"agentic_core/schemas/models/core_contracts.py"}

class ModelVisitor(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        is_pydantic = any(isinstance(base, ast.Name) and base.id in {"BaseModel", "RootModel"} for base in node.bases)
        is_contract = any(node.name.endswith(s) for s in CONTRACT_SIGNALS)
        has_dataclass = any(isinstance(d, ast.Name) and d.id == "dataclass" for d in node.decorator_list)

        if is_pydantic or (has_dataclass and is_contract):
            logger.error(f"BLOCKED: Inline contract '{node.name}' found at L{node.lineno}. Migrate to core_contracts.py.")
            sys.exit(1)
        self.generic_visit(node)

def main():
    for arg in sys.argv[1:]:
        if arg in EXEMPT or "tests/" in arg:
            logger.info(f"Skipping Exempt: {arg}")
            continue
        logger.info(f"Auditing: {arg}")
        with open(arg, "r", encoding="utf-8") as f:
            try:
                ModelVisitor().visit(ast.parse(f.read()))
            except Exception as e:
                logger.warning(f"Parse Warning in {arg}: {e}")

if __name__ == "__main__":
    main()
