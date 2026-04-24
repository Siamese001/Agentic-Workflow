"""W3 discovery: build replacement-target map for 21 low-fan-in DEPRECATED agents.

Reads each target file's docstring to identify the replacement hint, then queries
the ADG SQLite snapshot for consumer list via resolves_callsite edges.
Writes: artifacts/agent_deprecation/w3_replacement_map.json
"""
from __future__ import annotations

import json
import pathlib
import re
import sqlite3
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
ADG = REPO / "artifacts" / "adg" / "adg_indexed_04242026_0721.sqlite"
OUT = REPO / "artifacts" / "agent_deprecation" / "w3_replacement_map.json"

# 21 low-fan-in DEPRECATED agents from W0 assessment
# fan-in range 2-8
TARGETS = [
    "agentic_core/L3_orchestration/reasoning/CoverageAgent.py",
    "agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py",
    "agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py",
    "agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py",
    "agentic_core/L5_safety/reasoning/CodeFormatterAgent.py",
    "agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py",
    "agentic_core/L5_safety/reasoning/CodeJanitorAgent.py",
    "agentic_core/L1_cognition/reasoning/StrategicRecommendationAgent.py",
    "agentic_core/L2_execution/reasoning/ToolsmithAgent.py",
    "agentic_core/L5_safety/reasoning/BenchmarkingAgent.py",
    "agentic_core/L5_safety/reasoning/BootstrapAgent.py",
    "agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py",
    "agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py",
    "agentic_core/L5_safety/reasoning/CostGovernorAgent.py",
    "agentic_core/L5_safety/reasoning/ArchitectureGovernorValidatorAgent.py",
    "agentic_core/L5_safety/reasoning/CodeDetectorAgent.py",
    "agentic_core/L5_safety/reasoning/DependencyPruningAgent.py",
    "agentic_core/L3_orchestration/reasoning/GravityStateAgent.py",
    "agentic_core/L5_safety/reasoning/CodeValidatorAgent.py",
    "agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py",
    "agentic_core/L5_safety/reasoning/CredentialScannerAgent.py",
]


REPLACEMENT_PATTERNS = [
    # "Use X instead." / "use X.Y instead"
    re.compile(r"[Uu]se\s+([a-zA-Z_][\w\.]+)\s+instead"),
    re.compile(r"[Rr]eplaced?\s+by\s+([a-zA-Z_][\w\.]+)"),
    re.compile(r"[Mm]igrat\w+\s+to\s+([a-zA-Z_][\w\.]+)"),
    re.compile(r"[Ss]ee\s+([a-zA-Z_][\w\.]+)\s+for\s+(?:the\s+)?replacement"),
    re.compile(r"[Cc]onsolidated\s+into\s+([a-zA-Z_][\w\.]+)"),
    re.compile(r"[Mm]oved\s+to\s+([a-zA-Z_][\w\.]+)"),
]


def extract_docstring_head(path: pathlib.Path, max_lines: int = 40) -> str:
    """Return the first contiguous module docstring block of a file."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""
    # Find first triple-quote
    m = re.search(r'"""(.*?)"""', text, re.DOTALL)
    if not m:
        return ""
    doc = m.group(1)
    lines = doc.splitlines()[:max_lines]
    return "\n".join(lines).strip()


def infer_replacement(doc: str) -> str | None:
    for pat in REPLACEMENT_PATTERNS:
        m = pat.search(doc)
        if m:
            return m.group(1).rstrip(".,:;")
    return None


def classify_complexity(lines: int, fanin: int) -> str:
    if fanin <= 3 and lines < 100:
        return "trivial"
    if fanin <= 6 and lines < 200:
        return "low"
    return "medium"


def main() -> int:
    if not ADG.exists():
        sys.stderr.write(f"ADG snapshot missing: {ADG}\n")
        return 1
    conn = sqlite3.connect(str(ADG))
    cur = conn.cursor()

    entries = []
    for rel_path in TARGETS:
        abs_path = REPO / rel_path
        exists = abs_path.exists()
        lines = 0
        doc_head = ""
        replacement = None
        if exists:
            text = abs_path.read_text(encoding="utf-8", errors="replace")
            lines = text.count("\n") + 1
            doc_head = extract_docstring_head(abs_path)
            replacement = infer_replacement(doc_head)

        # Find the agent node by file_path, then incoming resolves_callsite edges
        consumers: list[str] = []
        fanin = 0
        try:
            cur.execute(
                "SELECT id FROM nodes WHERE file_path = ? LIMIT 5",
                (rel_path,),
            )
            node_ids = [r[0] for r in cur.fetchall()]
            if node_ids:
                placeholders = ",".join("?" * len(node_ids))
                cur.execute(
                    f"SELECT DISTINCT src.file_path FROM edges e "  # nosec B608 - fixed arity
                    f"JOIN nodes src ON e.src_id = src.id "
                    f"WHERE e.tgt_id IN ({placeholders}) "
                    f"  AND e.relation_type = 'resolves_callsite' "
                    f"LIMIT 50",
                    node_ids,
                )
                consumers = sorted({r[0] for r in cur.fetchall() if r[0]})
                fanin = len(consumers)
        except sqlite3.DatabaseError as exc:
            consumers = [f"<adg_query_error: {exc}>"]

        entries.append(
            {
                "agent_path": rel_path,
                "exists_on_disk": exists,
                "file_lines": lines,
                "docstring_head": doc_head,
                "inferred_replacement": replacement,
                "consumer_fanin": fanin,
                "consumer_files": consumers,
                "complexity": classify_complexity(lines, fanin),
            }
        )
    conn.close()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({"total": len(entries), "entries": entries}, indent=2),
        encoding="utf-8",
    )
    print(f"[ok] wrote {OUT}")
    print(f"[ok] {len(entries)} agents analyzed")
    found = sum(1 for e in entries if e["inferred_replacement"])
    print(f"[ok] {found}/{len(entries)} have inferred replacement targets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
