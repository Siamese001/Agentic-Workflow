"""Probe the A12 regexes."""

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.generate.truth_expansion_enricher import (
    GATE_DOCSTRING_CLAIM_RE,
    GATE_SQL_CLAUSE_RE,
    _gate_self_check,
)
from pathlib import Path
import tempfile
import textwrap

# Test fixture: real drift case
src = textwrap.dedent(
    '''"""Gate — queries relation_type='calls' for call-graph analysis."""
def run(conn):
    return conn.execute(
        "SELECT * FROM edges WHERE relation_type = 'writes_to'"
    )
'''
)
print("=== source ===")
print(src)
print("=== GATE_DOCSTRING_CLAIM_RE on first 60 lines ===")
head = "\n".join(src.splitlines()[:60])
print("docstring matches:", GATE_DOCSTRING_CLAIM_RE.findall(head))
print("\n=== GATE_SQL_CLAUSE_RE on body ===")
# Simulate _strip_module_docstring behavior
import ast

tree = ast.parse(src)
first = tree.body[0]
if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
    end_line = first.end_lineno or first.lineno
    body = "\n".join(src.splitlines()[end_line:])
else:
    body = src
print("body after stripping module docstring:")
print(body)
print("sql matches:", GATE_SQL_CLAUSE_RE.findall(body))

# Run _gate_self_check
with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
    f.write(src)
    tmp_path = Path(f.name)
print("\n=== _gate_self_check result ===")
print(_gate_self_check(tmp_path))
tmp_path.unlink()
