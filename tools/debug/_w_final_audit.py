"""Audit the 12 remaining agents for actual DEPRECATION status + replacement hint."""

from __future__ import annotations

import json
import logging
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
OUT = REPO / "artifacts" / "agent_deprecation" / "w_final_audit.json"

TARGETS = [
    # W3.3
    "agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py",
    "agentic_core/L5_safety/reasoning/CodeJanitorAgent.py",
    "agentic_core/L5_safety/reasoning/CodeDetectorAgent.py",
    "agentic_core/L5_safety/reasoning/CodeValidatorAgent.py",
    "agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py",
    "agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py",
    # W4.2
    "agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py",
    "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
    "agentic_core/L0_routing/reasoning/RootCustomsAgent.py",
    # W5
    "agentic_core/L5_safety/reasoning/GovernanceAgent.py",
    "agentic_core/L5_safety/reasoning/LocationHealerAgent.py",
    "agentic_core/L5_safety/reasoning/FileClassificationAgent.py",
]

report = []
for rel in TARGETS:
    abs_path = REPO / rel
    if not abs_path.exists():
        report.append({"path": rel, "exists": False})
        continue
    text = abs_path.read_text(encoding="utf-8", errors="replace")
    lines = text.count("\n") + 1

    # Top docstring
    doc = ""
    m = re.search(r'^(?:#[^\n]*\n)*("""|\'\'\')(.*?)(\1)', text, re.DOTALL)
    if m:
        doc = m.group(2).strip()[:500]

    # Classification
    has_deprecated_banner = bool(re.search(r"DEPRECATED:", doc, re.IGNORECASE))
    has_keep_banner = bool(re.search(r"DEPRECATION STATUS:\s*KEEP|KEEP\s*[-:]\s*", doc))
    has_facade = bool(re.search(r"facade|Facade", doc))
    # Use X instead
    repl_m = re.search(r"[Uu]se\s+([a-zA-Z_][\w\.]+)\s+instead", doc)
    use_x_instead = repl_m.group(1) if repl_m else None
    # Delegates to
    deleg_m = re.search(r"[Dd]elegat\w+\s+to\s+([a-zA-Z_][\w\.]+)", doc)
    delegates_to = deleg_m.group(1) if deleg_m else None

    # Count warning emission
    has_warn = "warnings.warn" in text and "DeprecationWarning" in text

    # Check first real code block
    non_doc_lines = [
        ln for ln in text.splitlines() if ln.strip() and not ln.strip().startswith(("#", '"', "'"))
    ][:3]
    category = "unknown"
    if has_keep_banner:
        category = "KEEP"
    elif use_x_instead:
        category = "deprecated-delegating-shim"
    elif has_facade and delegates_to:
        category = "facade-shell"
    elif has_deprecated_banner:
        category = "deprecated-banner-only"
    elif has_warn:
        category = "deprecated-via-warn"
    else:
        category = "no-deprecation-marker"

    report.append(
        {
            "path": rel,
            "file_lines": lines,
            "category": category,
            "use_x_instead": use_x_instead,
            "delegates_to": delegates_to,
            "has_deprecated_banner": has_deprecated_banner,
            "has_keep_banner": has_keep_banner,
            "has_facade": has_facade,
            "has_warn": has_warn,
            "doc_head": doc[:250],
            "first_code_lines": non_doc_lines,
        }
    )

OUT.write_text(json.dumps({"items": report}, indent=2), encoding="utf-8")
logging.info("C3 write receipt: tools/debug/_w_final_audit.py write side effect recorded")
print(f"[ok] wrote {OUT}")
for r in report:
    name = r["path"].split("/")[-1]
    cat = r.get("category", "?")
    repl = r.get("use_x_instead") or r.get("delegates_to") or ""
    print(f"  [{cat:30s}] {name:40s} {r.get('file_lines', 0):5d} lines  -> {repl}")
