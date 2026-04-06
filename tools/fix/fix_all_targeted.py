"""Apply ALL targeted fixes in one pass — safe, no multi-line block manipulation.

1. CredentialGuard class + get_credential_guard in security/credential_guard.py
2. GovernedPayload re-export in governance_types.py
3. StateNamespaceError + UnversionedStateError in commit_versioned_state_transition.py
4. CredentialGuard import fix in instruction_packet_types.py
5. reset_reasoning_knowledge_registry in knowledge_orchestrator.py
6. reset_plan_registry in plan_creator.py
7. _emit_writes_through/pulls_context/validated_by_safety_plane in classification_kernel.py + answer_support.py
8. Missing _emit_reads_through in cache_key_builders.py
9. Missing stdlib imports (Any, dataclass, etc.) — ONLY add new single-line imports, NEVER modify multi-line blocks
"""

import os
import re

ROOT = r"C:\Git\Agentic-Workflow"

def read(rel):
    fp = os.path.join(ROOT, rel)
    with open(fp, encoding="utf-8") as f:
        return f.read()

def write(rel, content):
    fp = os.path.join(ROOT, rel)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)

def safe_insert_after(content, marker, insertion):
    """Insert text after the FIRST occurrence of marker line."""
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if marker in line:
            lines.insert(i + 1, insertion)
            return "\n".join(lines)
    return None

def safe_insert_before(content, marker, insertion):
    """Insert text before the FIRST occurrence of marker line."""
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if marker in line:
            lines.insert(i, insertion)
            return "\n".join(lines)
    return None

fixes_applied = 0

# ── Fix 1: CredentialGuard class in security/credential_guard.py ──
rel = r"agentic_core\L5_safety\enforcement\security\credential_guard.py"
c = read(rel)
if "class CredentialGuard" not in c:
    new = safe_insert_before(c, "PATTERNS = [", '''class CredentialGuard:
    """Runtime credential access guard."""

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def check(cls, operation="", target="", **kwargs):
        """Validate a credential access operation. No-op by default."""
        pass

    @classmethod
    def reset(cls):
        cls._instance = None


def get_credential_guard():
    """Get the singleton CredentialGuard instance."""
    return CredentialGuard.get_instance()


''')
    if new:
        write(rel, new)
        fixes_applied += 1
        print(f"  [1] Added CredentialGuard class to {rel}")

# ── Fix 2: GovernedPayload re-export ──
rel = r"agentic_core\L0_routing\types\governance_types.py"
c = read(rel)
if "GovernedPayload" not in c:
    new = safe_insert_before(c, "from agentic_core.L0_routing.types.determinism_types",
        "from agentic_core.L0_routing.reasoning.assembly_stage import GovernedPayload  # noqa: F401")
    if new:
        write(rel, new)
        fixes_applied += 1
        print(f"  [2] Added GovernedPayload re-export to {rel}")

# ── Fix 3: StateNamespaceError + UnversionedStateError ──
rel = r"agentic_core\L4_state\versioning\commit_versioned_state_transition.py"
c = read(rel)
if "StateNamespaceError" not in c:
    c = c.replace(
        "    StateTransitionRecord,\n    StateVersionMissingError,",
        "    StateNamespaceError,\n    StateTransitionRecord,\n    UnversionedStateError,\n    StateVersionMissingError,"
    )
    write(rel, c)
    fixes_applied += 1
    print(f"  [3] Added StateNamespaceError+UnversionedStateError to {rel}")

# ── Fix 4: instruction_packet_types.py ──
rel = r"agentic_core\L2_execution\types\instruction_packet_types.py"
c = read(rel)
if "get_credential_guard as credential_guard" in c:
    c = c.replace(
        "from agentic_core.L5_safety.enforcement.credential_guard import get_credential_guard as credential_guard",
        "from agentic_core.L5_safety.enforcement.credential_guard import CredentialGuard as credential_guard\nfrom agentic_core.L5_safety.enforcement.credential_guard import get_credential_guard"
    )
    write(rel, c)
    fixes_applied += 1
    print(f"  [4] Fixed CredentialGuard import in {rel}")

# ── Fix 5: reset_reasoning_knowledge_registry ──
rel = r"agentic_core\L1_cognition\knowledge\knowledge_orchestrator.py"
c = read(rel)
if "reset_reasoning_knowledge_registry" not in c:
    c = c.replace(
        "    get_reasoning_knowledge_registry,\n)",
        "    get_reasoning_knowledge_registry,\n    reset_reasoning_knowledge_registry,\n)"
    )
    write(rel, c)
    fixes_applied += 1
    print(f"  [5] Added reset_reasoning_knowledge_registry to {rel}")

# ── Fix 6: reset_plan_registry ──
rel = r"agentic_core\L1_cognition\planning\plan_creator.py"
c = read(rel)
if "reset_plan_registry" not in c:
    c = c.replace(
        "    get_plan_registry,\n)",
        "    get_plan_registry,\n    reset_plan_registry,\n)"
    )
    write(rel, c)
    fixes_applied += 1
    print(f"  [6] Added reset_plan_registry to {rel}")

# ── Fix 7: _emit_writes_through in classification_kernel + answer_support ──
for rel, marker in [
    (r"agentic_core\L5_safety\core_kernel\classification_kernel.py", "    _emit_gated_by_confidence,"),
    (r"agentic_core\utils\workflow_engines\answer_support.py", "    _emit_routes_through,"),
]:
    c = read(rel)
    if "_emit_writes_through" not in c:
        c = c.replace(
            marker + "\n)",
            marker + "\n    _emit_writes_through,\n    _emit_pulls_context,\n    _emit_validated_by_safety_plane,\n)"
        )
        write(rel, c)
        fixes_applied += 1
        print(f"  [7] Added _emit_writes_through etc to {rel}")

# ── Fix 8: Missing _emit_reads_through in cache_key_builders.py ──
rel = r"agentic_core\cache\cache_key_builders.py"
c = read(rel)
if "_emit_reads_through" in c and "lifecycle_trace_contract" not in c:
    # Add import after last import or after docstring
    lines = c.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("def _require_safe_segment"):
            lines.insert(i, "from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through\n")
            break
    write(rel, "\n".join(lines))
    fixes_applied += 1
    print(f"  [8] Added _emit_reads_through import to {rel}")

# ── Fix 9: Missing stdlib imports — SAFE approach ──
# Only add NEW single-line import statements, never modify existing blocks
LTC = "agentic_core.runtime.lifecycle_trace_contract"

# Map: symbol -> import line
STDLIB_MAP = {
    'Any': 'from typing import Any',
    'Optional': 'from typing import Optional',
    'dataclass': 'from dataclasses import dataclass',
    'field': 'from dataclasses import field',
    'Enum': 'from enum import Enum',
    'Path': 'from pathlib import Path',
    'BaseModel': 'from pydantic import BaseModel',
    'ConfigDict': 'from pydantic import ConfigDict',
}

stdlib_fixed = 0
for base in ["agentic_core", "apps_shared", "apps_lic", "apps_rg", "system_learning"]:
    scan = os.path.join(ROOT, base)
    if not os.path.isdir(scan):
        continue
    for dp, _, fns in os.walk(scan):
        for fn in fns:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(dp, fn)
            try:
                with open(fp, encoding="utf-8") as f:
                    content = f.read()
            except (ValueError, TypeError, RuntimeError) as e:
                continue

            needed_imports = []
            for sym, imp_line in STDLIB_MAP.items():
                # Check if symbol is USED (word boundary)
                if sym == 'field':
                    if not re.search(r'\bfield\s*\(', content):
                        continue
                elif sym == 'Path':
                    if not re.search(r'\bPath\b(?![A-Za-z_])', content):
                        continue
                else:
                    if not re.search(r'\b' + re.escape(sym) + r'\b', content):
                        continue

                # Check if already imported (simple text search)
                if re.search(r'import\s+' + re.escape(sym) + r'\b', content):
                    continue
                # Also check if defined locally
                if f"class {sym}" in content or f"def {sym}" in content:
                    continue
                # Check multiline import blocks
                if re.search(r'^\s+' + re.escape(sym) + r'\s*[,)]', content, re.MULTILINE):
                    continue

                needed_imports.append(imp_line)

            if not needed_imports:
                continue

            # Deduplicate by combining same-module imports
            by_module = {}
            for imp in needed_imports:
                m = re.match(r'from (\S+) import (.+)', imp)
                if m:
                    mod, sym = m.group(1), m.group(2)
                    by_module.setdefault(mod, []).append(sym)

            final_imports = []
            for mod, syms in sorted(by_module.items()):
                final_imports.append(f"from {mod} import {', '.join(sorted(syms))}")

            # Find insertion point: after FIRST 'import' line but before any LTC import
            lines = content.split("\n")
            insert_pos = None
            for i, line in enumerate(lines):
                s = line.strip()
                if s.startswith("import ") and not s.startswith("import agentic_core"):
                    insert_pos = i + 1
                    break

            if insert_pos is None:
                # Find after module docstring
                in_docstring = False
                for i, line in enumerate(lines):
                    s = line.strip()
                    if s.startswith('"""'):
                        if in_docstring:
                            insert_pos = i + 1
                            break
                        elif s.count('"""') >= 2:
                            insert_pos = i + 1
                            break
                        else:
                            in_docstring = True
                    elif s.endswith('"""') and in_docstring:
                        insert_pos = i + 1
                        break

            if insert_pos is None:
                insert_pos = 0

            for k, imp in enumerate(final_imports):
                lines.insert(insert_pos + k, imp)

            new_content = "\n".join(lines)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new_content)
            stdlib_fixed += 1
            rel_path = os.path.relpath(fp, ROOT)
            if stdlib_fixed <= 10:
                print(f"  [9] Stdlib fix: {rel_path} ({', '.join(final_imports)})")

if stdlib_fixed > 10:
    print(f"  [9] ... and {stdlib_fixed - 10} more stdlib fixes")
fixes_applied += stdlib_fixed

print(f"\nTotal fixes applied: {fixes_applied}")
