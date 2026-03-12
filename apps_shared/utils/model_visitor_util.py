"""
Sovereign Guard: Block Inline Pydantic models (Final Sovereign Version)
Constitutional enforcement - all models must live in core_contracts_types.py
Signal-based filtering with timestamped, prefixed logging
"""
import ast
import logging
import sys
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger('sovereign.models')
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter('[MODELS] %(levelname)s %(asctime)s | %(message)s', '%H:%M:%S'))
Logger.addHandler(handler)
Logger.setLevel(logging.INFO)
contract_signals = ('Profile', 'Config', 'State', 'Context', 'Result', 'Message', 'Request', 'Response')
exempt = {'agentic_core/schemas/models/core_contracts_types.py'}

class ModelVisitor(ast.NodeVisitor):
    """Brief description of functionality and purpose."""

    def visit_ClassDef(self, node):
        is_pydantic = any((isinstance(base, ast.Name) and base.id in {'BaseModel', 'RootModel'} for base in node.bases))
        is_contract = any((node.name.endswith(s) for s in CONTRACT_SIGNALS))
        has_dataclass = any((isinstance(d, ast.Name) and d.id == 'dataclass' for d in node.decorator_list))
        if is_pydantic or (has_dataclass and is_contract):
            Logger.error(f"BLOCKED: Inline contract '{node.name}' found at L{node.lineno}. Migrate to core_contracts_types.py.")
            sys.exit(1)
        self.generic_visit(node)

def main():
    """Brief description of functionality and purpose."""
    for arg in sys.argv[1:]:
        if arg in EXEMPT or 'tests/' in arg:
            Logger.info(f'Skipping Exempt: {arg}')
            continue
        Logger.info(f'Auditing: {arg}')
        with open(arg, encoding='utf-8') as f:
            try:
                ModelVisitor().visit(ast.parse(f.read()))
            except Exception as e:
                raise
                Logger.warning(f'Parse Warning in {arg}: {e}')
if __name__ == '__main__':
    main()
