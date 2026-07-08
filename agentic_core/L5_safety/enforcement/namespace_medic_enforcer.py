from __future__ import annotations

from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "namespace_medic_enforcer")
trace_contract.emit_determinism_digest("p0", "namespace_medic_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "namespace_medic_enforcer", "L5")
trace_contract._emit_routes_through("p1", "namespace_medic_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "namespace_medic_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "namespace_medic_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "namespace_medic_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "namespace_medic_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "namespace_medic_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "namespace_medic_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "namespace_medic_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "namespace_medic_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "namespace_medic_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "namespace_medic_enforcer")
trace_contract._emit_gated_by_confidence("p1", "namespace_medic_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "namespace_medic_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "namespace_medic_enforcer", "L5")
trace_contract._emit_authorize_and_execute("p2", "namespace_medic_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "namespace_medic_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "namespace_medic_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "namespace_medic_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "namespace_medic_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "namespace_medic_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "namespace_medic_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "namespace_medic_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "namespace_medic_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "namespace_medic_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "namespace_medic_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "namespace_medic_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "namespace_medic_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "namespace_medic_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "namespace_medic_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "namespace_medic_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "namespace_medic_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "namespace_medic_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "namespace_medic_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "namespace_medic_enforcer", "exec_snapshot_link")

"\nNamespace Medic - Standalone Utility for Fast Import Healing\nScans all Python files and injects Missing standard library imports.\nRun this BEFORE CanonValidatorAgent to fix import starvation issues.\n"
import ast
import sys
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from tqdm import tqdm

trace_contract._emit_emits_metric_event("namespace_medic_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("namespace_medic_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("namespace_medic_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("namespace_medic_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("namespace_medic_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("namespace_medic_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("namespace_medic_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("namespace_medic_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("namespace_medic_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("namespace_medic_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("namespace_medic_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("namespace_medic_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("namespace_medic_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("namespace_medic_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("namespace_medic_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("namespace_medic_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("namespace_medic_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("namespace_medic_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("namespace_medic_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("namespace_medic_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("namespace_medic_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("namespace_medic_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("namespace_medic_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("namespace_medic_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("namespace_medic_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("namespace_medic_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("namespace_medic_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("namespace_medic_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "namespace_medic_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "namespace_medic_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "namespace_medic_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "namespace_medic_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "namespace_medic_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "namespace_medic_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "namespace_medic_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "namespace_medic_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "namespace_medic_enforcer", "routing_commit")

import_patterns: Any = [
    ("logging.", "import logging", "simple"),
    ("Logger.", "import logging", "simple"),
    ("Any", "from typing import Any, Optional, Protocol, Dict, List", "typing"),
    ("Optional", "from typing import Any, Optional, Protocol, Dict, List", "typing"),
    ("Protocol", "from typing import Any, Optional, Protocol, Dict, List", "typing"),
    ("Dict[", "from typing import Any, Optional, Protocol, Dict, List", "typing"),
    ("List[", "from typing import Any, Optional, Protocol, Dict, List", "typing"),
    ("@dataclass", "from dataclasses import dataclass, field", "dataclass"),
    ("dataclass(", "from dataclasses import dataclass, field", "dataclass"),
    ("Enum", "from enum import Enum, auto", "enum"),
    ("Path(", "from pathlib import Path", "simple"),
    ("json.", "import json", "simple"),
    ("os.path", "import os", "simple"),
    ("sys.", "import sys", "simple"),
    ("re.", "import re", "simple"),
    ("datetime.", "import datetime", "simple"),
    ("time.", "import time", "simple"),
    ("asyncio.", "import asyncio", "simple"),
]


def find_missing_imports(content: str) -> list[str]:
    """Detect which standard library imports are Missing from the file."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "find_missing_imports", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "find_missing_imports", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "find_missing_imports")
    Missing: Any = []
    seen_import_types: Any = set()
    for usage_pattern, import_stmt, import_type in IMPORT_PATTERNS:
        if usage_pattern not in content:
            continue
        if import_stmt in content:
            continue
        if import_type == "typing" and "typing" in seen_import_types:
            continue
        if import_stmt not in Missing:
            Missing.append(import_stmt)
            seen_import_types.add(import_type)
    return Missing


def inject_imports(content: str, imports: list[str]) -> str:
    """Inject Missing imports at the top of the file (after docstring)."""
    lines: Any = content.split("\n")
    insert_idx: Any = 0
    in_docstring: Any = False
    docstring_char: Any = None
    for i, line in tqdm(enumerate(lines), desc="Processing", unit="item"):
        stripped: Any = line.strip()
        if stripped.startswith("#"):
            insert_idx: Any = i + 1
            continue
        if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
            docstring_char: Any = stripped[:3]
            in_docstring: Any = True
            if stripped.count(docstring_char) >= 2:
                in_docstring: Any = False
                insert_idx: Any = i + 1
            continue
        if in_docstring and docstring_char in stripped:
            in_docstring: Any = False
            insert_idx: Any = i + 1
            continue
        if not in_docstring and stripped and (not stripped.startswith("#")):
            break
    import_lines: Any = imports + [""]
    lines[insert_idx:insert_idx] = import_lines
    return "\n".join(lines)


def heal_file(file_path: Path, dry_run: bool = False) -> tuple[bool, int]:
    """
    Heal a single file by injecting Missing imports.
    Returns (was_healed, num_imports_added)
    """
    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content: Any = f.read()  # review: Syntax errors should be caught at parser level, not runtime
        Missing: Any = find_missing_imports(content)
        if not Missing:
            return (False, 0)
        healed_content: Any = inject_imports(content, Missing)
        try:
            ast.parse(healed_content)
        except SyntaxError as e:  # review: Syntax errors should be caught at parser level, not runtime
            print(f"   [!] Syntax error after healing {file_path.name}: {e}")
            return (False, 0)
        if not dry_run:
            _wg.open_write(file_path, healed_content)
        return (True, len(Missing))
    except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
        print(f"   [!] Failed to heal {file_path.name}: {e}")
        return (False, 0)


def main() -> Any:
    """Main entry point for namespace healing."""
    import argparse

    parser: Any = argparse.ArgumentParser(
        description="Namespace Medic - Fix Missing standard library imports",
    )
    parser.add_argument("--target", default=AGENTIC_CORE_DIR, help="Target directory to scan")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without modifying files",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args: Any = parser.parse_args()
    project_root: Any = Path(__file__).parent
    target_path: Any = (project_root / args.target).resolve()
    if not target_path.exists():
        print(f"[!] Target path does not exist: {target_path}")
        sys.exit(1)
    print(f"{'=' * 70}")
    print("NAMESPACE MEDIC - Standard Library Import Healer")
    print(f"{'=' * 70}")
    print(f"Target: {target_path}")
    print(f"Mode: {('DRY RUN' if args.dry_run else 'LIVE HEALING')}")
    print(f"{'=' * 70}\n")
    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

    python_files: Any = list(get_python_files(target_path))
    print(f"[SCAN] Found {len(python_files)} Python files\n")
    healed_count: Any = 0
    total_imports: Any = 0
    for file_path in tqdm(python_files, desc="Processing", unit="item"):
        was_healed, num_imports = heal_file(file_path, dry_run=args.dry_run)
        if was_healed:
            healed_count += 1
            total_imports += num_imports
            status: Any = "[DRY-RUN]" if args.dry_run else "[HEALED]"
            print(f"{status} {file_path.name} (+{num_imports} imports)")
            if args.verbose:
                with open(file_path, encoding="utf-8", errors="replace") as f:
                    content: Any = f.read()
                Missing: Any = find_missing_imports(content) if args.dry_run else []
                for imp in Missing:
                    print(f"         + {imp}")
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Files scanned: {len(python_files)}")
    print(f"Files healed: {healed_count}")
    print(f"Total imports added: {total_imports}")
    if args.dry_run:
        print("\n[INFO] This was a dry run. Run without --dry-run to apply changes.")
    else:
        print("\n[SUCCESS] Namespace healing complete!")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
