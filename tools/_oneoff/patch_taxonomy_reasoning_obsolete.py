"""One-off: mark agent_taxonomy_registry apps_rg/reasoning entries OBSOLETE."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
p = REPO / "agentic_core/L2_execution/types/agent_taxonomy_registry.py"
text = p.read_text(encoding="utf-8")
note = "DELETED: apps-rg-reasoning-deletion-d4e8f1. File removed."


def patch_block(m: re.Match[str]) -> str:
    block = m.group(0)
    if "apps_rg/reasoning/" not in block:
        return block
    block = re.sub(r"status=AgentStatus\.\w+", "status=AgentStatus.OBSOLETE", block)
    block = re.sub(r"is_shim=(True|False)", "is_shim=True", block)
    block = re.sub(r"implements_l2_contract=(True|False)", "implements_l2_contract=False", block)
    if "notes=" in block:
        block = re.sub(r'notes="[^"]*"', f'notes="{note}"', block)
    return block


pat = r'"[^"]+": AgentClassification\(\s*[\s\S]*?\),\n'
new_text, n = re.subn(pat, patch_block, text)
p.write_text(new_text, encoding="utf-8")
print("patched_blocks", n)
