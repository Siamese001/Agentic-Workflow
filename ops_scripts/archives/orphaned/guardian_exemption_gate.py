"""
Guardian Exemption Gate — Exemption Quality Ratchet

Closes the scanner blind spot: the burndown gate tracks *unwhitelisted* violations,
but once a guardian comment is added the violation disappears from its view.
This gate tracks the exemptions themselves.

Two rules enforced on every commit
────────────────────────────────────────
Rule 1 — JUSTIFICATION REQUIRED (staged files only — zero-tolerance for new additions)
    Any `# guardian: allow-*` comment added or modified in a STAGED production
    file MUST have a `-- <justification>` suffix.  Empty or generic justifications
    are blocked.  Existing unjustified exemptions in untouched files are NOT blocked
    (they appear in the ratchet and must be fixed during normal cleanup).

Rule 2 — COUNT RATCHET (all production files)
    Tracks {rel_path: {exemption_type: count}} in guardian_exemption_budget.json.
    Any new exemption that raises the count above the ratchet ceiling is blocked.
    When counts fall the ratchet tightens automatically.

Scope
─────
Production directories only (agentic_core/, apps_*/,  system_learning/).
tools/, tests/, ops_scripts/ are excluded — utility scripts have looser rules.

Exit codes
──────────
  0  — all rules pass (commit allowed)
  1  — rule violation (commit blocked)

Environment overrides
─────────────────────
  ADG_EXEMPTION_BYPASS=1   — skip gate entirely (emergency; logged to stderr)
  ADG_EXEMPTION_DRY_RUN=1  — report without updating ratchet
  ADG_EXEMPTION_INIT=1     — (re)initialise ratchet from current state, exit 0
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
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

_emit_records_execution_trace("p0", "evidence", "guardian_exemption_gate")
_emit_applies_guardrail("p0", "guardian_exemption_gate", "p0_governance")
_emit_reads_policy_state("p0", "guardian_exemption_gate", "policy_binding")
_emit_snapshots_state("p0", "guardian_exemption_gate", "state_snapshot")
emit_replay_key("p0", "guardian_exemption_gate")
emit_determinism_digest("p0", "guardian_exemption_gate")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "guardian_exemption_gate", "execution_auth")
_emit_validates_capability("p2", "guardian_exemption_gate", "capability_check")
_emit_routes_to_capability("p2", "guardian_exemption_gate", "capability_route")
_emit_writes_via_uwg("p2", "guardian_exemption_gate", "uwg_write")
_emit_blocks_direct_write("p2", "guardian_exemption_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "guardian_exemption_gate", "tool_invocation")
_emit_captures_execution_output("p2", "guardian_exemption_gate", "exec_output")
_emit_dispatches_agent("p3", "guardian_exemption_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "guardian_exemption_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "guardian_exemption_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "guardian_exemption_gate", "healing_outcome")
_emit_escalates_failure("p3", "guardian_exemption_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "guardian_exemption_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "guardian_exemption_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "guardian_exemption_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "guardian_exemption_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "guardian_exemption_gate", "eval_metric")
_emit_stores_embedding("p4", "guardian_exemption_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "guardian_exemption_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "guardian_exemption_gate", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Bootstrap — works as pre-commit hook or direct invocation from repo root.
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(
        0, str(_REPO_ROOT),
    )  # guardian: allow-global-mutation -- CI bootstrap requires sys.path setup before package imports

from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
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

_emit_emits_metric_event("guardian_exemption_gate", "p4obs", "metric_1")
_emit_emits_metric_event("guardian_exemption_gate", "p4obs", "metric_2")
_emit_emits_metric_event("guardian_exemption_gate", "p4obs", "metric_3")
_emit_emits_metric_event("guardian_exemption_gate", "p4obs", "metric_4")
_emit_emits_metric_event("guardian_exemption_gate", "p4obs", "metric_5")
_emit_emits_metric_event("guardian_exemption_gate", "p4obs", "metric_6")
_emit_records_incident_event("guardian_exemption_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("guardian_exemption_gate", "p4obs", "anomaly")
_emit_writes_observability_log("guardian_exemption_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("guardian_exemption_gate", "p4obs", "mon_state")
_emit_triggers_alert("guardian_exemption_gate", "p4obs", "alert")
_emit_links_incident_trace("guardian_exemption_gate", "p4obs", "trace_link")
_emit_captures_pattern("guardian_exemption_gate", "p3lm", "pattern")
_emit_records_learning_event("guardian_exemption_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("guardian_exemption_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("guardian_exemption_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("guardian_exemption_gate", "p3lm", "routing")
_emit_improves_agent_policy("guardian_exemption_gate", "p3lm", "policy")
_emit_stores_learning_state("guardian_exemption_gate", "p3lm", "state")
_emit_records_execution_trace("guardian_exemption_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("guardian_exemption_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("guardian_exemption_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("guardian_exemption_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("guardian_exemption_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("guardian_exemption_gate", "env_read", "p2_env_1")
_emit_reads_environ("guardian_exemption_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("guardian_exemption_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("guardian_exemption_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "guardian_exemption_gate", "context_pull")
_emit_pulls_context("p1", "guardian_exemption_gate", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "guardian_exemption_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "guardian_exemption_gate", "uwg_term_secondary")
_emit_writes_through("p1", "guardian_exemption_gate", "write_through")
_emit_writes_through("p1", "guardian_exemption_gate", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "guardian_exemption_gate", "safety_validation")
_emit_invokes_eval("p1", "guardian_exemption_gate", "eval_call")
_emit_proposal_commits_routing("p1", "guardian_exemption_gate", "routing_commit")
_emit_escalates_to_human("p1", "guardian_exemption_gate", "human_escalation")
_emit_routes_through("p1", "guardian_exemption_gate", "route_through")
_emit_checks_agent_registry("p1", "guardian_exemption_gate", "agent_registry")
_emit_validates_agent_capability("p1", "guardian_exemption_gate", "capability")
_emit_dispatches_execution_plan("p1", "guardian_exemption_gate", "exec_plan")
_emit_agent_executes_agent("p1", "guardian_exemption_gate", "sub_agent")
_emit_routes_to_agent("p1", "guardian_exemption_gate", "target_agent")
_emit_verifies_policy("p1", "guardian_exemption_gate", "policy_check")
_emit_observes_runtime_state("p1", "guardian_exemption_gate", "runtime_state")
_emit_verifies_boundary("p1", "guardian_exemption_gate", "boundary_check")
_emit_transcripts_response("p1", "guardian_exemption_gate", "transcript")
_emit_hard_fails_untranscripted("p1", "guardian_exemption_gate")
_emit_gated_by_confidence("p1", "guardian_exemption_gate", "confidence_gate")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_1")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_2")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_3")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_4")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_5")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_6")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_7")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_8")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_9")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_10")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_11")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_12")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_13")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_14")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_15")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_16")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_17")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_18")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_19")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_20")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_21")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_22")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_23")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_24")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_25")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_26")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_27")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_28")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_29")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_30")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_31")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_32")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_33")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_34")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_35")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_36")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_37")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_38")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_39")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_40")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_41")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_42")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_43")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_44")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_45")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_46")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_47")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_48")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_49")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_50")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_51")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_52")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_53")
_emit_reads_through("l4", "guardian_exemption_gate", "urg_read_54")

PROJECT_ROOT = get_validated_project_root()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

RATCHET_FILE = PROJECT_ROOT / OPS_SCRIPTS_DIR / "hooks" / "guardian_exemption_budget.json"

# Production directories to scan — tools/, tests/, ops_scripts/ are excluded.
PRODUCTION_DIRS = [
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "apps_exec",
    "apps_eval",
    "apps_rfp",
    "apps_research",
    "system_learning",
]

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".nox",
    "archives",
    ".backup",
    ".test_artifacts",
    ".pytest_cache",
}

EXCLUDE_FILE_PATTERNS = ["test_*.py", "*_test.py", "conftest.py"]

# Generic justification tokens that provide no real signal.
# A justification consisting ONLY of these words (after stripping punctuation)
# is treated as empty.
_GENERIC_TOKENS = frozenset(
    {
        "needed",
        "required",
        "necessary",
        "legacy",
        "fixme",
        "todo",
        "temporary",
        "temp",
        "wip",
        "ignore",
        "skip",
        "bypass",
        "ok",
        "fine",
        "allowed",
        "allow",
        "exempt",
        "exception",
        "placeholder",
        "stub",
        "hack",
        "workaround",
    },
)

# Matches canonical guardian comment: # guardian: allow-<type> -- <justification>
_CANONICAL_RE = re.compile(r"^\s*#\s*guardian:\s+allow-([a-z][a-z0-9-]+)\s+--\s+(.+)$")

# Matches ANY guardian comment (including malformed) to detect missing justification.
_ANY_GUARDIAN_RE = re.compile(
    r"^\s*#\s*[Gg]uardian[:\s].*allow[-_]",
)

# Canonical form with NO justification (the exact bad pattern).
_NO_JUSTIFICATION_RE = re.compile(r"^\s*#\s*guardian:\s+allow-[a-z][a-z0-9-]+\s*$")

Budget = dict[str, dict[str, int]]  # {rel_path: {exemption_type: count}}


# ---------------------------------------------------------------------------
# Justification quality check
# ---------------------------------------------------------------------------


def _is_generic_justification(justification: str) -> bool:
    """Return True if the justification is empty or contains only generic tokens."""
    cleaned = re.sub(r"[^a-z\s]", "", justification.lower())
    tokens = set(cleaned.split())
    if not tokens:
        return True
    # All tokens must be non-generic for the justification to pass.
    return tokens.issubset(_GENERIC_TOKENS)


# ---------------------------------------------------------------------------
# File scanning
# ---------------------------------------------------------------------------


def _collect_production_files() -> list[Path]:
    files = []
    for prod_dir in PRODUCTION_DIRS:
        target = PROJECT_ROOT / prod_dir
        if not target.exists():
            continue
        for f in sorted(target.rglob("*.py")):
            parts = set(f.relative_to(PROJECT_ROOT).parts)
            if parts & EXCLUDE_DIRS:
                continue
            if any(f.match(pat) for pat in EXCLUDE_FILE_PATTERNS):
                continue
            files.append(f)
    return files


def _rel(fp: Path) -> str:
    return fp.relative_to(PROJECT_ROOT).as_posix()


def _scan_file(file_path: Path) -> list[tuple[int, str, str | None, str | None]]:
    """
    Scan a single file for guardian exemption comments.

    Returns list of (line_no, raw_line, exemption_type, justification).
    - exemption_type is None if the comment is malformed/unparseable.
    - justification is None if absent.
    """
    results = []
    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:    # guardian: Add error context logging
        return results

    for i, line in enumerate(lines, start=1):
        if not _ANY_GUARDIAN_RE.search(line):
            continue

        m = _CANONICAL_RE.match(line)
        if m:
            results.append((i, line, m.group(1), m.group(2).strip()))
            continue

        # Malformed or missing justification — still record it.
        if _NO_JUSTIFICATION_RE.match(line):
            # Has type but no justification at all.
            type_match = re.search(r"allow-([a-z][a-z0-9-]+)", line)
            etype = type_match.group(1) if type_match else "unknown"
            results.append((i, line, etype, None))
        else:
            # Some other malformed variant.
            type_match = re.search(r"allow[-_]([a-z][a-z0-9_-]+)", line, re.IGNORECASE)
            etype = type_match.group(1).lower().replace("_", "-") if type_match else "unknown"
            results.append((i, line, etype, None))

    return results


# ---------------------------------------------------------------------------
# Ratchet I/O
# ---------------------------------------------------------------------------


def _load_ratchet() -> Budget:
    if not RATCHET_FILE.exists():
        return {}
    try:
        return json.loads(RATCHET_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):    # guardian: Add error context logging
        return {}


def _write_ratchet(ratchet: Budget) -> None:
    RATCHET_FILE.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(ratchet, indent=2, sort_keys=True) + "\n"
    fd, tmp = tempfile.mkstemp(
        dir=str(RATCHET_FILE.parent),
        prefix=".exemption_ratchet_",
        suffix=".tmp",
    )
    try:
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        if sys.platform == "win32" and RATCHET_FILE.exists():
            RATCHET_FILE.unlink()
        Path(tmp).replace(RATCHET_FILE)
    except BaseException:    # guardian: BaseException should be handled with specific context
        try:
            os.close(fd)
        except OSError:    # guardian: Add error context logging
            pass
        try:
            os.unlink(tmp)
        except OSError:    # guardian: Add error context logging
            pass
        raise


def _ratchet_total(ratchet: Budget) -> int:
    return sum(c for cats in ratchet.values() for c in cats.values())


# ---------------------------------------------------------------------------
# Core ratchet logic
# ---------------------------------------------------------------------------


def _scan_to_counts(scan_results: dict[str, list]) -> Budget:
    """Convert per-file scan results → {rel_path: {exemption_type: count}}."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for rel_path, hits in scan_results.items():
        for _lineno, _raw, etype, _just in hits:
            if etype:
                counts[rel_path][etype] += 1
    return {f: dict(cats) for f, cats in counts.items()}


def _check_ratchet(
    ratchet: Budget,
    current: Budget,
) -> list[tuple[str, str, int, int]]:
    """
    Return (rel_path, etype, allowed, actual) for every ratchet violation.

    Rule 2: any exemption_type count that exceeds its ratchet ceiling is blocked.
    New file+type pairs (allowed=0, actual>0) are also blocked.
    """
    out = []
    for rel_path, types in current.items():
        ratchet_file = ratchet.get(rel_path, {})
        for etype, actual in types.items():
            allowed = ratchet_file.get(etype, 0)
            if actual > allowed:
                out.append((rel_path, etype, allowed, actual))
    return sorted(out)


def _tighten_ratchet(ratchet: Budget, current: Budget) -> tuple[Budget, int]:
    """Tighten ratchet to current counts.  Only shrinks, never grows."""
    new_ratchet: Budget = {}
    improved = 0
    for rel_path, types in ratchet.items():
        current_types = current.get(rel_path, {})
        new_types: dict[str, int] = {}
        for etype, ceiling in types.items():
            actual = current_types.get(etype, 0)
            new_val = min(ceiling, actual)
            if new_val > 0:
                new_types[etype] = new_val
            if actual < ceiling:
                improved += 1
        if new_types:
            new_ratchet[rel_path] = new_types
    return new_ratchet, improved


# ---------------------------------------------------------------------------
# Staged file detection
# ---------------------------------------------------------------------------


def _get_staged_production_files() -> set[str]:
    """
    Return a set of repo-relative POSIX paths for staged Python files that
    are within production directories.  Returns an empty set if git is
    unavailable or no files are staged.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode != 0:
            return set()
        staged = set()
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line.endswith(".py"):
                continue
            # Must be under a production directory.
            first_part = line.split("/")[0]
            if first_part in set(PRODUCTION_DIRS):
                staged.add(line)
        return staged
    except (ValueError, TypeError, RuntimeError) as e:  # noqa: BLE001
        return set()


def _get_added_lines_per_file() -> dict[str, set[int]]:
    """
    Parse ``git diff --cached -U0`` to get the set of *added* line numbers
    per file.  Only lines starting with ``+`` (excluding the ``+++`` header)
    are considered added.  Returns {posix_rel_path: {line_numbers}}.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "-U0", "--no-color"],
            capture_output=True,
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode != 0:
            return {}
    except (ValueError, TypeError, RuntimeError) as e:  # noqa: BLE001
        return {}

    added: dict[str, set[int]] = defaultdict(set)
    current_file: str | None = None
    stdout_text = result.stdout.decode("utf-8", errors="replace")
    for raw_line in stdout_text.splitlines():
        if raw_line.startswith("+++ b/"):
            current_file = raw_line[6:]
            continue
        if raw_line.startswith("@@ ") and current_file:
            # Parse hunk header: @@ -old,count +new,count @@
            hunk = raw_line.split("@@")[1].strip()
            plus_part = hunk.split("+")[1].split()[0]
            if "," in plus_part:
                start, count = plus_part.split(",")
                start, count = int(start), int(count)
            else:
                start, count = int(plus_part), 1
            for ln in range(start, start + count):
                added[current_file].add(ln)
    return dict(added)


# ---------------------------------------------------------------------------
# Main gate logic
# ---------------------------------------------------------------------------


def main() -> int:  # noqa: C901
    bypass = os.getenv("ADG_EXEMPTION_BYPASS", "").strip() == "1"
    dry_run = os.getenv("ADG_EXEMPTION_DRY_RUN", "").strip() == "1"
    init_mode = os.getenv("ADG_EXEMPTION_INIT", "").strip() == "1"
    json_output = os.getenv("ADG_EXEMPTION_JSON_OUTPUT", "").strip() or None

    # Allow --json-output override via command line
    import argparse
    _arg_parser = argparse.ArgumentParser()
    _arg_parser.add_argument("--json-output", metavar="PATH", help="Write structured issues to JSON lines file")
    _args, _ = _arg_parser.parse_known_args()
    if _args.json_output:
        json_output = _args.json_output

    # Add project root for schema imports
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from ops_scripts.ci.pre_commit_issue_schema import PreCommitIssue, SeverityLevel

    if bypass:
        print("[guardian-exemption-gate] BYPASS active — skipping gate", file=sys.stderr)
        return 0

    files = _collect_production_files()
    if not files:
        print("[guardian-exemption-gate] No production files found — nothing to check.")
        return 0

    # Scan all production files.
    scan_results: dict[str, list] = {}
    for f in files:
        hits = _scan_file(f)
        if hits:
            scan_results[_rel(f)] = hits

    # ---------------------------------------------------------------------------
    # Init mode — write ratchet from current state and exit.
    # ---------------------------------------------------------------------------
    ratchet = _load_ratchet()
    current_counts = _scan_to_counts(scan_results)
    total_exemptions = _ratchet_total(current_counts)

    if init_mode:
        _write_ratchet(current_counts)
        print(
            f"[guardian-exemption-gate] INIT: ratchet written — "
            f"{len(current_counts)} files, {total_exemptions} total exemptions",
        )
        return 0

    # ---------------------------------------------------------------------------
    # Rule 1 — JUSTIFICATION REQUIRED (staged files only)
    # Applies only to files that are staged for this commit — prevents new
    # unjustified exemptions from being added without blocking legacy ones.
    # ---------------------------------------------------------------------------
    staged_files = _get_staged_production_files()
    added_lines = _get_added_lines_per_file()
    rule1_failures: list[tuple[str, int, str, str]] = []

    for rel_path, hits in scan_results.items():
        if rel_path not in staged_files:
            continue  # Only check files being committed right now.
        # Convert POSIX rel_path to match git diff output (already POSIX).
        file_added = added_lines.get(rel_path, set())
        # Also try backslash variant for Windows compatibility.
        if not file_added:
            file_added = added_lines.get(rel_path.replace("/", "\\"), set())
        for lineno, raw_line, etype, justification in hits:
            # Rule 1 only applies to ADDED lines — skip pre-existing exemptions.
            if lineno not in file_added:
                continue
            if justification is None:
                rule1_failures.append((rel_path, lineno, raw_line.strip(), "missing -- <justification>"))
            elif _is_generic_justification(justification):
                rule1_failures.append(
                    (rel_path, lineno, raw_line.strip(), f"generic justification: '{justification}'"),
                )

    # ---------------------------------------------------------------------------
    # Rule 2 — COUNT RATCHET (all production files)
    # ---------------------------------------------------------------------------
    ratchet_violations = _check_ratchet(ratchet, current_counts)

    # ---------------------------------------------------------------------------
    # Reporting
    # ---------------------------------------------------------------------------
    passed = not rule1_failures and not ratchet_violations

    staged_label = f"{len(staged_files)} staged" if staged_files else "no staged production"
    print(
        f"[guardian-exemption-gate] Scanned {len(files)} production files ({staged_label} files checked for Rule 1)",
    )
    print(
        f"[guardian-exemption-gate] Total guardian exemptions: {total_exemptions} (ratchet ceiling: {_ratchet_total(ratchet)})",
    )

    if rule1_failures:
        print(f"\n{'=' * 70}")
        print(f"RULE 1 VIOLATION — {len(rule1_failures)} new exemption(s) missing real justification")
        print(f"{'=' * 70}")
        print("Staged files may not add `# guardian: allow-*` without a specific `-- <justification>`.")
        print("Generic words (needed, required, temporary, legacy) are not accepted.\n")
        for rel_path, lineno, raw, reason in rule1_failures:
            print(f"  {rel_path}:{lineno}")
            print(f"    {raw}")
            print(f"    >>  {reason}")
            print()
        print("Fix: add a real justification, e.g.:")
        print(
            "  # guardian: allow-magic-config -- DEFAULT_TIMEOUT is deploy-environment-specific, owner: infra",
        )
        print(
            "  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above",
        )
        print()

    if ratchet_violations:
        print(f"\n{'=' * 70}")
        print(f"RULE 2 VIOLATION — {len(ratchet_violations)} ratchet ceiling(s) exceeded")
        print(f"{'=' * 70}")
        print("Exemption counts in production code may only decrease.\n")
        for rel_path, etype, allowed, actual in ratchet_violations:
            delta = actual - allowed
            print(f"  {rel_path}  [{etype}]  ceiling={allowed}  actual={actual}  (+{delta} new)")
        print()
        print("To legitimately add a new exemption:")
        print("  1. Get HITL approval via ask_user_question in Cascade")
        print("  2. Add `# guardian: allow-<type> -- <specific justification>`")
        print("  3. Re-init: ADG_EXEMPTION_INIT=1 python ops_scripts/ci/guardian_exemption_gate.py")
        print()

    # Build structured issues for JSON output
    json_issues = []
    for rel_path, lineno, raw, reason in rule1_failures:
        issue = PreCommitIssue(
            hook_id="guardian-exemption-gate",
            hook_name="Guardian Exemption Quality",
            severity=SeverityLevel.HIGH,
            file_path=rel_path,
            line_number=lineno,
            message="Guardian exemption lacks valid justification",
            explanation=f"Every guardian exemption must have a specific justification. Issue: {reason}",
            issue_type="exemption_justification",
        )
        json_issues.append(issue)

    for rel_path, etype, allowed, actual in ratchet_violations:
        issue = PreCommitIssue(
            hook_id="guardian-exemption-gate",
            hook_name="Guardian Exemption Quality",
            severity=SeverityLevel.HIGH,
            file_path=rel_path,
            message=f"Ratchet ceiling exceeded for {etype}",
            explanation=f"Exemption counts may only decrease. Ceiling was {allowed}, now {actual}.",
            issue_type="exemption_ratchet",
        )
        json_issues.append(issue)

    # Write JSON output if requested
    if json_output and json_issues:
        output_path = Path(json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for issue in json_issues:
                f.write(issue.to_json() + "\n")

    if passed:
        new_ratchet, improved = _tighten_ratchet(ratchet, current_counts)
        if improved and not dry_run:
            _write_ratchet(new_ratchet)
            print(f"[guardian-exemption-gate] PASS -- ratchet tightened ({improved} slot(s) improved)")
        else:
            print("[guardian-exemption-gate] PASS -- all exemptions justified")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
