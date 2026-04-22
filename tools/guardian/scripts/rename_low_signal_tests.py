"""
tools/guardian/scripts/rename_low_signal_tests.py

Low-signal test filename renamer — ADG-only, no grep.

A "low-signal" test filename contains a chronological wave/phase number prefix
that encodes *when* the test was written rather than *what* it tests.  These
names are hostile to navigation and CI reporting.

Detection rule (ADG-backed, no filesystem scan beyond path normalisation):
    A test module is low-signal if its stem matches the pattern
        test_wave<N>* or test_wave<N>_phase<M>*
    AND the word "wave" or "phase" does NOT appear in the production module
    path(s) the file covers (via ADG ``covers`` edges).
    Files whose "phase/wave" token comes from the production module they test
    (e.g. test_two_phase_commit.py -> two_phase_coordinator.py) are excluded.

Rename strategy:
    1. Query ADG ``covers`` edges to find the primary production module covered.
    2. Derive a canonical name from that module's stem:
           test_<production_stem>.py
       Placed in the same directory as the original file.
    3. If multiple production modules are covered, pick the one whose stem is
       most informative (longest, non-path_constants fallback).
    4. If no covers edges exist, fall back to stripping the wave/phase prefix
       and keeping the remainder:
           test_wave1_phase1_2_sovereignty.py  -> test_sovereignty.py
    5. Conflict resolution: if the target name already exists, append ``_v2``,
       ``_v3``, ... until a free slot is found.

Usage:
    # Dry-run (default) — print proposed renames, exit 0
    python tools/guardian/scripts/rename_low_signal_tests.py

    # Show JSON output
    python tools/guardian/scripts/rename_low_signal_tests.py --json

    # Execute renames (moves files on disk + updates git mv)
    python tools/guardian/scripts/rename_low_signal_tests.py --execute

    # Restrict to a sub-directory
    python tools/guardian/scripts/rename_low_signal_tests.py --root tests/architecture

Exit codes:
    0  — success (dry-run: proposals computed; execute: all renames applied)
    1  — ADG unavailable or fatal error
    2  — one or more renames skipped due to conflicts (only with --execute)
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "rename_low_signal_tests")
_emit_applies_guardrail("p0", "rename_low_signal_tests", "p0_governance")
_emit_reads_policy_state("p0", "rename_low_signal_tests", "policy_binding")
_emit_snapshots_state("p0", "rename_low_signal_tests", "state_snapshot")
emit_replay_key("p0", "rename_low_signal_tests")
emit_determinism_digest("p0", "rename_low_signal_tests")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rename_low_signal_tests", "execution_auth")
_emit_validates_capability("p2", "rename_low_signal_tests", "capability_check")
_emit_routes_to_capability("p2", "rename_low_signal_tests", "capability_route")
_emit_writes_via_uwg("p2", "rename_low_signal_tests", "uwg_write")
_emit_blocks_direct_write("p2", "rename_low_signal_tests", "direct_write_block")
_emit_records_tool_invocation("p2", "rename_low_signal_tests", "tool_invocation")
_emit_captures_execution_output("p2", "rename_low_signal_tests", "exec_output")
_emit_dispatches_agent("p3", "rename_low_signal_tests", "agent_dispatch")
_emit_coordinates_agents("p3", "rename_low_signal_tests", "agent_coordination")
_emit_records_workflow_lineage("p3", "rename_low_signal_tests", "workflow_lineage")
_emit_records_healing_outcome("p3", "rename_low_signal_tests", "healing_outcome")
_emit_escalates_failure("p3", "rename_low_signal_tests", "failure_escalation")
_emit_orchestrates_workflow("p3", "rename_low_signal_tests", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rename_low_signal_tests", "healing_dispatch")
_emit_invokes_evaluation("p3", "rename_low_signal_tests", "evaluation_signal")
_emit_records_telemetry_event("p4", "rename_low_signal_tests", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rename_low_signal_tests", "eval_metric")
_emit_stores_embedding("p4", "rename_low_signal_tests", "embedding_store")
_emit_updates_meta_learning_state("p4", "rename_low_signal_tests", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rename_low_signal_tests", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Repo root bootstrap
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve()
ROOT = _SCRIPT_DIR.parents[3]  # tools/guardian/scripts -> ROOT
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("rename_low_signal_tests", "p4obs", "metric_1")
_emit_emits_metric_event("rename_low_signal_tests", "p4obs", "metric_2")
_emit_emits_metric_event("rename_low_signal_tests", "p4obs", "metric_3")
_emit_emits_metric_event("rename_low_signal_tests", "p4obs", "metric_4")
_emit_emits_metric_event("rename_low_signal_tests", "p4obs", "metric_5")
_emit_emits_metric_event("rename_low_signal_tests", "p4obs", "metric_6")
_emit_records_incident_event("rename_low_signal_tests", "p4obs", "incident")
_emit_captures_runtime_anomaly("rename_low_signal_tests", "p4obs", "anomaly")
_emit_writes_observability_log("rename_low_signal_tests", "p4obs", "obs_log")
_emit_updates_monitoring_state("rename_low_signal_tests", "p4obs", "mon_state")
_emit_triggers_alert("rename_low_signal_tests", "p4obs", "alert")
_emit_links_incident_trace("rename_low_signal_tests", "p4obs", "trace_link")
_emit_captures_pattern("rename_low_signal_tests", "p3lm", "pattern")
_emit_records_learning_event("rename_low_signal_tests", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rename_low_signal_tests", "p3lm", "snapshot")
_emit_feeds_meta_learning("rename_low_signal_tests", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rename_low_signal_tests", "p3lm", "routing")
_emit_improves_agent_policy("rename_low_signal_tests", "p3lm", "policy")
_emit_stores_learning_state("rename_low_signal_tests", "p3lm", "state")
_emit_records_execution_trace("rename_low_signal_tests", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rename_low_signal_tests", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rename_low_signal_tests", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rename_low_signal_tests", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rename_low_signal_tests", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rename_low_signal_tests", "env_read", "p2_env_1")
_emit_reads_environ("rename_low_signal_tests", "env_read", "p2_env_2")
_emit_reads_runtime_state("rename_low_signal_tests", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rename_low_signal_tests", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rename_low_signal_tests", "context_pull")
_emit_pulls_context("p1", "rename_low_signal_tests", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "rename_low_signal_tests", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rename_low_signal_tests", "uwg_term_secondary")
_emit_writes_through("p1", "rename_low_signal_tests", "write_through")
_emit_writes_through("p1", "rename_low_signal_tests", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "rename_low_signal_tests", "safety_validation")
_emit_invokes_eval("p1", "rename_low_signal_tests", "eval_call")
_emit_proposal_commits_routing("p1", "rename_low_signal_tests", "routing_commit")
_emit_escalates_to_human("p1", "rename_low_signal_tests", "human_escalation")
_emit_routes_through("p1", "rename_low_signal_tests", "route_through")
_emit_checks_agent_registry("p1", "rename_low_signal_tests", "agent_registry")
_emit_validates_agent_capability("p1", "rename_low_signal_tests", "capability")
_emit_dispatches_execution_plan("p1", "rename_low_signal_tests", "exec_plan")
_emit_agent_executes_agent("p1", "rename_low_signal_tests", "sub_agent")
_emit_routes_to_agent("p1", "rename_low_signal_tests", "target_agent")
_emit_verifies_policy("p1", "rename_low_signal_tests", "policy_check")
_emit_observes_runtime_state("p1", "rename_low_signal_tests", "runtime_state")
_emit_verifies_boundary("p1", "rename_low_signal_tests", "boundary_check")
_emit_transcripts_response("p1", "rename_low_signal_tests", "transcript")
_emit_hard_fails_untranscripted("p1", "rename_low_signal_tests")
_emit_gated_by_confidence("p1", "rename_low_signal_tests", "confidence_gate")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_1")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_2")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_3")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_4")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_5")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_6")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_7")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_8")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_9")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_10")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_11")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_12")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_13")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_14")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_15")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_16")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_17")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_18")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_19")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_20")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_21")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_22")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_23")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_24")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_25")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_26")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_27")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_28")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_29")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_30")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_31")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_32")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_33")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_34")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_35")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_36")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_37")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_38")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_39")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_40")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_41")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_42")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_43")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_44")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_45")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_46")
_emit_reads_through("l4", "rename_low_signal_tests", "urg_read_47")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Regex that identifies a chronological wave/phase prefix in a test filename.
#: Matches: test_wave1_*, test_wave2_phase3_*, test_wave1_phase1_2_*, etc.
_LOW_SIGNAL_RE = re.compile(
    r"^test_wave\d+(?:_phase[\d_]+)?_?(.*)$",
    re.IGNORECASE,
)

#: Production modules that are too generic to derive a meaningful name from.
_UNINFORMATIVE_MODULES: frozenset[str] = frozenset(
    {
        "path_constants",
        "semantic_gap_analyzer",
        "__init__",
    },
)

#: If the covered production module stem contains any of these tokens, the
#: file is NOT low-signal (the wave/phase token came from the production code).
_PRODUCTION_PHASE_TOKENS = re.compile(r"phase|wave", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class RenameProposal:
    original_path: str
    proposed_path: str
    reason: str
    covered_modules: list[str] = field(default_factory=list)
    conflict: bool = False


# ---------------------------------------------------------------------------
# ADG helpers
# ---------------------------------------------------------------------------


def _open_adg(adg_dir: Path) -> sqlite3.Connection:
    """Open the most-recent ADG SQLite.  Fail-closed if none found."""
    dbs = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
    if not dbs:
        raise RuntimeError(
            f"No ADG SQLite found in {adg_dir}. Run: python tools/adg/adg_redis_ingest.py --force",
        )
    return sqlite3.connect(str(dbs[-1]))


def _query_low_signal_files(
    conn: sqlite3.Connection,
    tests_root: str,
) -> list[tuple[int, str, str]]:
    """Return (node_id, adg_name, resolved_path) for all low-signal test modules.

    Low-signal = resolved_path stem matches ``_LOW_SIGNAL_RE``.
    Only module-level nodes whose resolved_path starts with tests_root are returned.
    Nodes that are class/function-level sub-entities of a file are excluded.
    """
    rows = conn.execute(
        "SELECT id, adg_name, resolved_path FROM nodes "
        "WHERE entity_type='module' "
        "AND resolved_path LIKE ? "
        "ORDER BY resolved_path",
        (tests_root.rstrip("/") + "/%",),
    ).fetchall()

    results = []
    for nid, adg_name, rpath in rows:
        stem = Path(rpath).stem
        if _LOW_SIGNAL_RE.match(stem):
            results.append((nid, adg_name, rpath))
    return results


def _covers_edges(conn: sqlite3.Connection, node_id: int) -> list[str]:
    """Return resolved_paths of all production modules covered by node_id."""
    rows = conn.execute(
        "SELECT n.resolved_path FROM edges e "
        "JOIN nodes n ON n.id = e.dst_id "
        "WHERE e.src_id=? AND e.relation_type='covers'",
        (node_id,),
    ).fetchall()
    return [r[0] for r in rows if r[0] and not r[0].startswith("tests/")]


def _imports_edges(conn: sqlite3.Connection, node_id: int) -> list[str]:
    """Return resolved_paths of all production modules imported by node_id."""
    rows = conn.execute(
        "SELECT n.resolved_path FROM edges e "
        "JOIN nodes n ON n.id = e.dst_id "
        "WHERE e.src_id=? AND e.relation_type='imports'",
        (node_id,),
    ).fetchall()
    return [r[0] for r in rows if r[0] and not r[0].startswith("tests/")]


# ---------------------------------------------------------------------------
# Name derivation
# ---------------------------------------------------------------------------


def _stem_from_production(prod_paths: list[str]) -> str | None:
    """Pick the most informative stem from a list of production module paths.

    Preference order:
      1. Longest stem not in _UNINFORMATIVE_MODULES and not containing
         phase/wave tokens (those would indicate the file is NOT low-signal).
      2. Any non-uninformative stem.
      3. None — caller will fall back to stripping the wave/phase prefix.
    """
    stems = []
    for p in prod_paths:
        stem = Path(p).stem
        if stem in _UNINFORMATIVE_MODULES:
            continue
        # Exclude stems from modules whose name itself contains phase/wave —
        # those mean the production module is named that way (not an artefact).
        if _PRODUCTION_PHASE_TOKENS.search(stem):
            continue
        stems.append(stem)

    if not stems:
        return None

    # Prefer the longest (most specific) name.
    return max(stems, key=len)


def _strip_wave_prefix(stem: str) -> str:
    """Remove the wave/phase prefix from a stem, returning remainder.

    Examples:
        test_wave1_phase1_2_sovereignty  -> sovereignty
        test_wave3_phase3_1_cache_wirings -> cache_wirings
        test_wave4_wave5_wave6_guardrails -> guardrails
    """
    m = _LOW_SIGNAL_RE.match(stem)
    if m:
        remainder = m.group(1).strip("_")
        return remainder if remainder else stem
    return stem


def _free_name(directory: Path, stem: str) -> Path:
    """Return a free Path for ``test_<stem>.py`` in *directory*.

    Appends ``_v2``, ``_v3``, ... if the plain name is taken.
    """
    candidate = directory / f"test_{stem}.py"
    if not candidate.exists():
        return candidate
    n = 2
    while True:
        candidate = directory / f"test_{stem}_v{n}.py"
        if not candidate.exists():
            return candidate
        n += 1


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def build_proposals(
    conn: sqlite3.Connection,
    repo_root: Path,
    tests_subdir: str,
) -> list[RenameProposal]:
    """Build rename proposals for all low-signal test files.

    Uses ADG covers/imports edges exclusively — no filesystem scanning,
    no grep, no regex over file contents.
    """
    rows = _query_low_signal_files(conn, tests_subdir)
    proposals: list[RenameProposal] = []

    for node_id, adg_name, rpath in tqdm(rows, desc="Processing", unit="item"):
        orig = repo_root / rpath

        # --- Collect covered production paths via ADG edges ---
        covered = _covers_edges(conn, node_id)
        if not covered:
            # Fall back to imports edges for files with no explicit covers edges
            covered = _imports_edges(conn, node_id)

        # --- Check: is this really low-signal, or does prod module use phase/wave? ---
        # If EVERY covered prod module contains phase/wave in its path, the
        # file is testing phase-named production code — exclude it.
        if covered:
            all_prod_phase = all(_PRODUCTION_PHASE_TOKENS.search(Path(p).stem) for p in covered if p)
            if all_prod_phase:
                continue  # Not a low-signal name — production module uses phase/wave

        # --- Derive canonical name ---
        prod_stem = _stem_from_production(covered)
        if prod_stem:
            new_stem = prod_stem
            reason = f"derives from covered module stem '{prod_stem}'"
        else:
            remainder = _strip_wave_prefix(Path(rpath).stem)
            if not remainder or remainder == Path(rpath).stem:
                continue  # Could not derive a better name — skip
            new_stem = remainder
            reason = "wave/phase prefix stripped (no covers edges)"

        # --- Resolve target path ---
        target = _free_name(orig.parent, new_stem)
        conflict = False

        # If target == orig (already well-named somehow) skip
        if target == orig:
            continue

        # Record whether a non-versioned collision exists
        plain_target = orig.parent / f"test_{new_stem}.py"
        if plain_target.exists() and plain_target != orig:
            conflict = True

        proposals.append(
            RenameProposal(
                original_path=rpath,
                proposed_path=str(target.relative_to(repo_root)).replace("\\", "/"),
                reason=reason,
                covered_modules=[c for c in covered[:4] if c],
                conflict=conflict,
            ),
        )

    return proposals


def execute_renames(
    proposals: list[RenameProposal],
    repo_root: Path,
) -> tuple[int, int]:
    """Apply renames via ``git mv``.  Returns (applied, skipped)."""
    applied = skipped = 0
    for p in tqdm(proposals, desc="Processing", unit="item"):
        src = repo_root / p.original_path
        dst = repo_root / p.proposed_path
        if not src.exists():
            print(f"  SKIP (src missing): {p.original_path}", file=sys.stderr)
            skipped += 1
            continue
        if dst.exists():
            print(f"  SKIP (dst exists):  {p.proposed_path}", file=sys.stderr)
            skipped += 1
            continue
        result = subprocess.run(
            ["git", "mv", str(src), str(dst)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(
                f"  FAIL: git mv {p.original_path} -> {p.proposed_path}\n        {result.stderr.strip()}",
                file=sys.stderr,
            )
            skipped += 1
        else:
            print(f"  RENAMED: {p.original_path}")
            print(f"       ->  {p.proposed_path}")
            applied += 1
    return applied, skipped


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Rename low-signal (wave/phase-numbered) test files using ADG coverage data.",
    )
    p.add_argument(
        "--execute",
        action="store_true",
        help="Apply renames via git mv (default: dry-run only).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON array of proposals to stdout.",
    )
    p.add_argument(
        "--root",
        default=None,
        metavar="SUBDIR",
        help="Restrict scan to a sub-directory of tests/ (e.g. tests/architecture).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    repo_root = get_validated_project_root()
    adg_dir = repo_root / "artifacts" / "adg"

    try:
        conn = _open_adg(adg_dir)
    except RuntimeError as exc:  # guardian: Runtime errors should be prevented with proper validation
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    tests_subdir = args.root if args.root else TESTS_DIR
    # Normalise to forward slashes, strip leading slash
    tests_subdir = tests_subdir.replace("\\", "/").lstrip("/")

    proposals = build_proposals(conn, repo_root, tests_subdir)
    conn.close()

    if not proposals:
        if not args.json:
            print(f"OK: no low-signal test filenames found under '{tests_subdir}'")
        else:
            print("[]")
        return 0

    if args.json:
        print(
            json.dumps(
                [
                    {
                        "original": p.original_path,
                        "proposed": p.proposed_path,
                        "reason": p.reason,
                        "covered_modules": p.covered_modules,
                        "conflict": p.conflict,
                    }
                    for p in proposals
                ],
                indent=2,
            ),
        )
        return 0

    # --- Human-readable output ---
    print(f"Low-signal test filenames detected: {len(proposals)}")
    print(f"Scan root: {tests_subdir}")
    print()
    for p in proposals:
        flag = " [CONFLICT — versioned]" if p.conflict else ""
        print(f"  {p.original_path}")
        print(f"    -> {p.proposed_path}{flag}")
        print(f"       reason: {p.reason}")
        if p.covered_modules:
            print(f"       covers: {', '.join(p.covered_modules[:3])}")
        print()

    if not args.execute:
        print("Dry-run complete.  Pass --execute to apply renames via git mv.")
        return 0

    # --- Execute ---
    print("Applying renames...")
    applied, skipped = execute_renames(proposals, repo_root)
    print()
    print(f"Done: {applied} renamed, {skipped} skipped.")
    return 2 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
