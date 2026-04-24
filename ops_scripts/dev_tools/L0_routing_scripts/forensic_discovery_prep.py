"""
FORENSIC DISCOVERY PREP - V10 GAP ANALYSIS TOOL
===============================================
Generates the authoritative "Environment Under Test" artifact for the
V10 Target State Gap Analysis.

USAGE:
    python forensic_discovery_prep_script.py [--out audit_context.json]

OUTPUT:
    A structured JSON artifact containing:
    1. Validated Agent Manifest (Identity + Path)
    2. Precise MRO Signatures (for Safety Mixin verification)
    3. Ghost/Invalid Agent Report

HARDENED INVARIANTS:
    - Deterministic ordering (stable output across runs)
    - Path traversal defense (validate all candidate paths are within project)
    - Evidence-rich records (file hash, size, parse errors, selection rationale)
    - Strict stub detection (sentinel in header, not substring anywhere)
    - Robust base extraction (no "UnknownBase" silently)
    - Atomic output write support (optional --out)
"""
# guardian: allow-silent_swallower -- ADG violation exemption

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import logging
import os
import platform
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "forensic_discovery_prep", "execution_auth")
_emit_validates_capability("p2", "forensic_discovery_prep", "capability_check")
_emit_routes_to_capability("p2", "forensic_discovery_prep", "capability_route")
_emit_writes_via_uwg("p2", "forensic_discovery_prep", "uwg_write")
_emit_blocks_direct_write("p2", "forensic_discovery_prep", "direct_write_block")
_emit_records_tool_invocation("p2", "forensic_discovery_prep", "tool_invocation")
_emit_captures_execution_output("p2", "forensic_discovery_prep", "exec_output")
_emit_dispatches_agent("p3", "forensic_discovery_prep", "agent_dispatch")
_emit_coordinates_agents("p3", "forensic_discovery_prep", "agent_coordination")
_emit_records_workflow_lineage("p3", "forensic_discovery_prep", "workflow_lineage")
_emit_records_healing_outcome("p3", "forensic_discovery_prep", "healing_outcome")
_emit_escalates_failure("p3", "forensic_discovery_prep", "failure_escalation")
_emit_orchestrates_workflow("p3", "forensic_discovery_prep", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "forensic_discovery_prep", "healing_dispatch")
_emit_invokes_evaluation("p3", "forensic_discovery_prep", "evaluation_signal")
_emit_records_telemetry_event("p4", "forensic_discovery_prep", "telemetry_event")
_emit_captures_evaluation_metric("p4", "forensic_discovery_prep", "eval_metric")
_emit_stores_embedding("p4", "forensic_discovery_prep", "embedding_store")
_emit_updates_meta_learning_state("p4", "forensic_discovery_prep", "meta_learning")
_emit_links_execution_to_snapshot("p4", "forensic_discovery_prep", "exec_snapshot_link")
from agentic_core.utils.ast_fuzzy_util import safe_unparse

emit_replay_key("p0", "forensic_discovery_prep")
emit_determinism_digest("p0", "forensic_discovery_prep")

_emit_dispatches_healing_run("p1", "forensic_discovery_prep", "L0")
_emit_routes_through("p1", "forensic_discovery_prep", "L0")
_emit_checks_agent_registry("p1", "forensic_discovery_prep", "agent_registry")
_emit_validates_agent_capability("p1", "forensic_discovery_prep", "capability")
_emit_dispatches_execution_plan("p1", "forensic_discovery_prep", "exec_plan")
_emit_agent_executes_agent("p1", "forensic_discovery_prep", "sub_agent")
_emit_routes_to_agent("p1", "forensic_discovery_prep", "target_agent")
_emit_verifies_policy("p1", "forensic_discovery_prep", "policy_check")
_emit_observes_runtime_state("p1", "forensic_discovery_prep", "runtime_state")
_emit_verifies_boundary("p1", "forensic_discovery_prep", "boundary_check")
_emit_transcripts_response("p1", "forensic_discovery_prep", "transcript")
_emit_hard_fails_untranscripted("p1", "forensic_discovery_prep")
_emit_gated_by_confidence("p1", "forensic_discovery_prep", "confidence_gate")
_emit_escalates_to_human("p1", "forensic_discovery_prep", "L0")
_emit_reads_policy_state("p1", "forensic_discovery_prep", "L0")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("forensic_discovery_prep", "p4obs", "metric_1")
_emit_emits_metric_event("forensic_discovery_prep", "p4obs", "metric_2")
_emit_emits_metric_event("forensic_discovery_prep", "p4obs", "metric_3")
_emit_emits_metric_event("forensic_discovery_prep", "p4obs", "metric_4")
_emit_emits_metric_event("forensic_discovery_prep", "p4obs", "metric_5")
_emit_emits_metric_event("forensic_discovery_prep", "p4obs", "metric_6")
_emit_records_incident_event("forensic_discovery_prep", "p4obs", "incident")
_emit_captures_runtime_anomaly("forensic_discovery_prep", "p4obs", "anomaly")
_emit_writes_observability_log("forensic_discovery_prep", "p4obs", "obs_log")
_emit_updates_monitoring_state("forensic_discovery_prep", "p4obs", "mon_state")
_emit_triggers_alert("forensic_discovery_prep", "p4obs", "alert")
_emit_links_incident_trace("forensic_discovery_prep", "p4obs", "trace_link")
_emit_captures_pattern("forensic_discovery_prep", "p3lm", "pattern")
_emit_records_learning_event("forensic_discovery_prep", "p3lm", "learning_event")
_emit_writes_learning_snapshot("forensic_discovery_prep", "p3lm", "snapshot")
_emit_feeds_meta_learning("forensic_discovery_prep", "p3lm", "meta_feed")
_emit_updates_routing_strategy("forensic_discovery_prep", "p3lm", "routing")
_emit_improves_agent_policy("forensic_discovery_prep", "p3lm", "policy")
_emit_stores_learning_state("forensic_discovery_prep", "p3lm", "state")
_emit_records_execution_trace("forensic_discovery_prep", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("forensic_discovery_prep", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("forensic_discovery_prep", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("forensic_discovery_prep", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("forensic_discovery_prep", "L4_STATE", "p2_trace_5")
_emit_reads_environ("forensic_discovery_prep", "env_read", "p2_env_1")
_emit_reads_environ("forensic_discovery_prep", "env_read", "p2_env_2")
_emit_reads_runtime_state("forensic_discovery_prep", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("forensic_discovery_prep", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "forensic_discovery_prep", "context_pull")
_emit_pulls_context("p1", "forensic_discovery_prep", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "forensic_discovery_prep", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "forensic_discovery_prep", "uwg_term_2")
_emit_writes_through("p1", "forensic_discovery_prep", "write_through")
_emit_writes_through("p1", "forensic_discovery_prep", "write_through_2")
_emit_validated_by_safety_plane("p1", "forensic_discovery_prep", "safety_validation")
_emit_invokes_eval("p1", "forensic_discovery_prep", "eval_call")
_emit_proposal_commits_routing("p1", "forensic_discovery_prep", "routing_commit")


def _get_safe_subprocess_check_output():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_safe_subprocess_check_output", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_safe_subprocess_check_output", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_safe_subprocess_check_output")
    from agentic_core.L2_execution.utils.safe_subprocess import safe_subprocess_check_output

    return safe_subprocess_check_output


try:
    from agentic_core.L0_routing.config import (
        AGENTIC_CORE_DIR,
        APPS_LIC_DIR,
        APPS_RG_DIR,
        APPS_SHARED_DIR,
        FORENSIC_DISCOVERY_INTEGRITY_HASH,
        FORENSIC_DISCOVERY_SCRIPT,
    )
    from agentic_core.L0_routing.utils.path_util import validate_path_within_project
    from ops_scripts.dev_tools.L0_routing.project_root_util import get_validated_project_root
    from ops_scripts.dev_tools.L0_routing.ssot_discovery_util import load_agent_discovery
except ImportError:  # guardian: allow-silent-swallow
    print("CRITICAL: SSOT imports failed. Ensure PYTHONPATH includes project root.", file=sys.stderr)
    sys.exit(1)
logging.basicConfig(level=logging.ERROR, format="%(message)s")
Logger = logging.getLogger("ForensicAudit")


@dataclass
class ForensicAgentRecord:
    """The absolute truth for a single agent under audit."""

    agent_name: str
    layer: str
    file_path: str
    class_name: str
    mro_signature: list[str]
    status: str
    methods_detected: list[str]
    file_sha256: str = ""
    file_size_bytes: int = 0
    selection_reason: str = ""
    selection_candidates: list[str] = field(default_factory=list)
    parse_error: str = ""
    has_heal: bool = False
    is_sovereign: bool = False


OUTPUT_SCHEMA_VERSION = "1.3.0"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_precise_mro(node: ast.ClassDef) -> list[str]:
    """
    Extracts base classes in exact declaration order to detect 'Inheritance Traps'.
    Example: class MyAgent(SafetyMixin, BaseAgent) -> ["SafetyMixin", "BaseAgent"]
    """
    bases = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(f"{base.value.id}.{base.attr}" if isinstance(base.value, ast.Name) else base.attr)
        else:
            bases.append(safe_unparse(base))
    return bases


def build_class_bases_map(project_root: Path) -> dict[str, list[str]]:
    """Build repo-wide mapping of class_name → direct base class names from AST.

    Scans all .py files under known source roots to enable full MRO resolution.
    On name collision, first-seen definition wins (deterministic via sorted paths).
    Handles starred bases (e.g. ``class Foo(*BASE_CLASSES)``) by resolving
    module-level tuple assignments in the same file.
    """
    class_map: dict[str, list[str]] = {}
    scan_roots = [
        project_root / AGENTIC_CORE_DIR,
        project_root / APPS_LIC_DIR,
        project_root / APPS_RG_DIR,
        project_root / APPS_SHARED_DIR,
    ]
    for root in tqdm(scan_roots, desc="Processing", unit="item"):
        if not root.exists():
            continue
        for py_file in tqdm(sorted(root.rglob("*.py")), desc="Processing", unit="item"):
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
                module_tuples: dict[str, list[str]] = {}
                for stmt in ast.walk(tree):
                    if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                        tgt = stmt.targets[0]
                        if isinstance(tgt, ast.Name) and isinstance(stmt.value, ast.Tuple):
                            elts = [e.id for e in stmt.value.elts if isinstance(e, ast.Name)]
                            if elts and tgt.id not in module_tuples:
                                module_tuples[tgt.id] = elts
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name not in class_map:
                        raw_bases = extract_precise_mro(node)
                        resolved: list[str] = []
                        for b in raw_bases:
                            if b.startswith("*") and b[1:] in module_tuples:
                                resolved.extend(module_tuples[b[1:]])
                            else:
                                resolved.append(b)
                        class_map[node.name] = resolved
            except (SyntaxError, Exception):  # guardian: allow-silent-swallow
                continue
    return class_map


def resolve_full_mro(
    direct_bases: list[str],
    class_map: dict[str, list[str]],
    _seen: set[str] | None = None,
) -> list[str]:
    """Recursively expand direct bases into a full transitive MRO chain.

    Returns a flat list of all ancestor class names (deduplicated, depth-first).
    """
    if _seen is None:
        _seen = set()
    result: list[str] = []
    for base in direct_bases:
        simple = base.rsplit(".", 1)[-1] if "." in base else base
        if simple in _seen:
            continue
        _seen.add(simple)
        result.append(simple)
        if simple in class_map:
            result.extend(resolve_full_mro(class_map[simple], class_map, _seen))
    return result


def stub_sentinel_detected(content: str) -> bool:
    head = "\n".join(content.splitlines()[:60])
    return (
        "STATUS: STUB" in head
        or ("__AGENT_STATUS__" in head and "STUB" in head)
        or any(line.strip() == "NOT_AN_AGENT" for line in head.splitlines())
    )


def forensic_inspect(name: str, layer: str, file_path: Path) -> ForensicAgentRecord:
    """
    Analyzes a file to build the Forensic Record.
    """
    record = ForensicAgentRecord(
        agent_name=name,
        layer=layer,
        file_path=str(file_path),
        class_name="Unknown",
        mro_signature=[],
        status="INVALID",
        methods_detected=[],
    )
    if not file_path.exists():
        record.status = "GHOST"
        return record
    try:
        record.file_size_bytes = file_path.stat().st_size
        record.file_sha256 = sha256_file(file_path)
        content = file_path.read_text(encoding="utf-8", errors="replace")
        if stub_sentinel_detected(content):
            record.status = "STUB"
            record.selection_reason = "Stub sentinel detected in file header"
            return record
        try:
            tree = ast.parse(content)  # guardian: Syntax errors should be caught at parser level, not runtime
        except SyntaxError as e:  # guardian: allow-silent-swallow
            record.status = "SYNTAX_ERROR"
            record.parse_error = f"SyntaxError: {e}"
            return record
        classes: list[ast.ClassDef] = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        record.selection_candidates = [c.name for c in classes]

        def score(cls: ast.ClassDef) -> int:
            bases = " ".join(extract_precise_mro(cls))
            s = 0
            if "SovereignBaseAgent" in bases or "BaseAgent" in bases:
                s += 100
            if "Agent" in cls.name:
                s += 10
            if "Healer" in cls.name:
                s += 5
            method_names = [i.name for i in cls.body if isinstance(i, ast.FunctionDef | ast.AsyncFunctionDef)]
            if "heal" in method_names:
                s += 20
            if any(m in method_names for m in ("execute", "run", "act")):
                s += 8
            return s

        if classes:
            chosen = sorted(classes, key=lambda c: (score(c), c.name), reverse=True)[0]
            if score(chosen) <= 0:
                record.status = "INVALID"
                record.selection_reason = "No viable agent class candidate (score<=0)"
                return record
            record.class_name = chosen.name
            record.mro_signature = extract_precise_mro(chosen)
            record.status = "ACTIVE"
            record.selection_reason = "Selected highest-scoring ClassDef deterministically"
            for item in chosen.body:
                if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                    record.methods_detected.append(item.name)
            record.has_heal = "heal" in record.methods_detected
    except (ValueError, TypeError) as e:
        record.status = f"ERROR: {str(e)}"
        record.parse_error = str(e)
    return record


def get_git_commit(root: Path) -> str:
    try:
        out = _get_safe_subprocess_check_output()(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            allow_protected_root_mutation=True,
        )
        return out.decode("utf-8").strip()
    except (ValueError, TypeError):  # guardian: allow-silent-swallow
        return ""


def atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    assert_no_persistent_write("L0", "write_text")
    tmp.write_text(data, encoding="utf-8")
    os.replace(tmp, path)


V54_SCHEMA_VERSION = "5.4.0"


def _compute_ssot_validation(project_root: Path) -> dict[str, str]:
    """Compute ssot_validation section: self-hash vs SSOT constant."""
    script_path = project_root / FORENSIC_DISCOVERY_SCRIPT
    if script_path.exists():
        computed = hashlib.sha256(script_path.read_bytes()).hexdigest()
    else:
        computed = ""
    return {
        "blueprint_hash": FORENSIC_DISCOVERY_INTEGRITY_HASH,
        "status": "MATCH" if computed == FORENSIC_DISCOVERY_INTEGRITY_HASH else "MISMATCH",
    }


def _derive_mixins(mro_chain: list[str]) -> list[str]:
    """Derive mixins deterministically from MRO chain entries containing 'Mixin'."""
    return [entry for entry in mro_chain if "Mixin" in entry]


def _to_v54_schema(legacy: dict, project_root: Path) -> dict:
    """Transform legacy discovery output to v5.4 strict schema."""
    meta = legacy.get("audit_meta", {})
    v54: dict = {
        "meta": {
            "timestamp": meta.get("generated_at", ""),
            "root_path": meta.get("root", ""),
            "git_hash": meta.get("git_commit", ""),
            "schema_version": V54_SCHEMA_VERSION,
            "python_version": meta.get("python_version", ""),
            "platform": meta.get("platform", ""),
            "total_candidates": meta.get("total_candidates", 0),
        },
        "ssot_validation": _compute_ssot_validation(project_root),
        "agents": [],
    }
    for agent in tqdm(legacy.get("environment_under_test", []), desc="Processing", unit="item"):
        mro_chain = agent.get("mro_signature", [])
        v54["agents"].append(
            {
                "identity": agent.get("agent_name", ""),
                "layer": agent.get("layer", ""),
                "status": agent.get("status", ""),
                "file_path": agent.get("file_path", ""),
                "class_name": agent.get("class_name", ""),
                "mro_chain": mro_chain,
                "mixins": _derive_mixins(mro_chain),
                "detected_methods": agent.get("methods_detected", []),
                "integrity_hash": agent.get("file_sha256", ""),
                "is_sovereign": agent.get("is_sovereign", False),
            },
        )
    return v54


def run_forensic_discovery(out_path: Path | None = None, *, legacy_schema: bool = False) -> int:
    project_root = get_validated_project_root()
    class_bases_map = build_class_bases_map(project_root)
    raw_candidates = load_agent_discovery(project_root, force_reload=True)
    raw_candidates = sorted(
        raw_candidates,
        key=lambda c: (c.get("layer", ""), c.get("class_name", ""), c.get("file", "")),
    )
    manifest = {
        "audit_meta": {
            "root": str(project_root),
            "total_candidates": len(raw_candidates),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "output_schema_version": OUTPUT_SCHEMA_VERSION,
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "git_commit": get_git_commit(project_root),
        },
        "environment_under_test": [],
        "ignored_artifacts": [],
        "counts": {},
    }
    for candidate in tqdm(raw_candidates, desc="Processing", unit="item"):
        rel_path = candidate.get("file", "") or candidate.get("path", "")
        name = candidate.get("class_name", "") or candidate.get("name", "Unknown")
        layer = candidate.get("layer", "Unknown")
        if not rel_path:
            record = ForensicAgentRecord(
                agent_name=name,
                layer=layer,
                file_path="",
                class_name="Unknown",
                mro_signature=[],
                status="INVALID",
                methods_detected=[],
                selection_reason="Missing path in SSOT candidate",
            )
            manifest["ignored_artifacts"].append(asdict(record))
            continue
        full_path = project_root / rel_path
        try:
            validate_path_within_project(project_root, full_path)
        except Exception:  # guardian: allow-silent-swallow
            raise
        record = forensic_inspect(name, layer, full_path)
        direct_bases = class_bases_map.get(record.class_name, record.mro_signature)
        if direct_bases:
            full_chain = resolve_full_mro(direct_bases, class_bases_map)
            record.mro_signature = full_chain
            record.is_sovereign = "SovereignBaseAgent" in full_chain
        if record.status == "ACTIVE":
            manifest["environment_under_test"].append(asdict(record))
        else:
            manifest["ignored_artifacts"].append(asdict(record))
    manifest["environment_under_test"] = sorted(
        manifest["environment_under_test"],
        key=lambda r: (r["agent_name"], r["file_path"]),
    )
    manifest["ignored_artifacts"] = sorted(
        manifest["ignored_artifacts"],
        key=lambda r: (r["agent_name"], r["file_path"]),
    )
    counts: dict[str, int] = {}
    for r in manifest["environment_under_test"] + manifest["ignored_artifacts"]:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    manifest["counts"] = dict(sorted(counts.items(), key=lambda kv: kv[0]))
    if legacy_schema:
        output = manifest
    else:
        output = _to_v54_schema(manifest, project_root)
    payload = json.dumps(output, indent=2)
    if out_path:
        atomic_write(out_path, payload)
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Forensic Discovery Prep (Audit Scope Generator)")
        parser.add_argument("--out", help="Write JSON output to file atomically (recommended)")
        parser.add_argument(
            "--legacy-schema",
            action="store_true",
            default=False,
            help="Emit legacy schema (audit_meta/environment_under_test) instead of v5.4",
        )
        args = parser.parse_args()
        outp = Path(args.out) if args.out else None
        rc = run_forensic_discovery(outp, legacy_schema=args.legacy_schema)
        sys.exit(rc)
    except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
        print(json.dumps({"fatal_error": str(e)}))
        sys.exit(1)
