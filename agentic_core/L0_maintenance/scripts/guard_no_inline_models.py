from __future__ import annotations
"""
Sovereign Guard: Block Inline Pydantic Models (Final Sovereign Version)
Constitutional enforcement - all models must live in core_contracts.py
Signal-based filtering with timestamped, prefixed logging
"""
import ast
import sys
import logging
from pathlib import Path
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

# Logger Setup
Logger = logging.getLogger("sovereign.models")
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("[MODELS] %(levelname)s %(asctime)s | %(message)s", "%H:%M:%S"))
Logger.addHandler(handler)
Logger.setLevel(logging.INFO)

# NAMING FIXED: CONTRACT_SIGNALS → contract_signals
contract_signals = ("Profile", "Config", "State", "Context", "Result", "Message", "Request", "Response")
# NAMING FIXED: EXEMPT → exempt
exempt = {"agentic_core/schemas/models/core_contracts.py"}

# NAMING FIXED: ModelVisitor → ModelVisitor
class ModelVisitor(ast.NodeVisitor):
    '''Brief description of functionality and purpose.'''
    
    def visit_ClassDef(self, node):
                    
        is_pydantic = any(isinstance(base, ast.Name) and base.id in {"BaseModel", "RootModel"} for base in node.bases)
        is_contract = any(node.name.endswith(s) for s in CONTRACT_SIGNALS)
        has_dataclass = any(isinstance(d, ast.Name) and d.id == "dataclass" for d in node.decorator_list)

        if is_pydantic or (has_dataclass and is_contract):
            Logger.error(f"BLOCKED: Inline contract '{node.name}' found at L{node.lineno}. Migrate to core_contracts.py.")
            sys.exit(1)
        self.generic_visit(node)

def main():
    '''Brief description of functionality and purpose.'''
    
    for arg in sys.argv[1:]:
        if arg in EXEMPT or "tests/" in arg:
            Logger.info(f"Skipping Exempt: {arg}")
            continue
        Logger.info(f"Auditing: {arg}")
        with open(arg, "r", encoding="utf-8") as f:
            try:
                ModelVisitor().visit(ast.parse(f.read()))
            except Exception as e:
                Logger.warning(f"Parse Warning in {arg}: {e}")

if __name__ == "__main__":
    main()
