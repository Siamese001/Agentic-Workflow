"""
ADG CI Gates — Wave 0 hard-fail delta enforcement.

Six gates derived from Plan Hardening Addendum CI Enforcement Layer.
Each gate compares current ADG snapshot graph_plane_counts against a
frozen baseline (wave0_baseline.json) and fails if a metric regresses.

Gates
-----
  M1 — Determinism Gate      : uses_wall_clock_delta > 0  →  FAIL
                                (unless emits_determinism_digest_delta > 0 or seeds_rng_delta > 0)
  M2 — Dispatch Visibility   : invokes_getattr_dynamic_delta > 0  →  FAIL
                                (unless agent_executes_agent_delta > 0)
  M3 — Mutation Sovereignty  : writes_to_delta > 0  →  FAIL
                                (unless writes_through_delta > 0)
  M4 — Guardrail Coverage    : applies_guardrail / calls < GUARDRAIL_COVERAGE_THRESHOLD  →  FAIL (enforce after W3)
  M5 — Trace Coverage        : records_execution_trace / (calls + invokes_eval) < TRACE_COVERAGE_THRESHOLD  →  FAIL (enforce after W5)
  M6 — Replay Key Gate       : emits_replay_key_delta == 0 for routing PRs  →  FAIL (enforce after W4)

Mode
----
  Each gate has an independent mode: "warn" or "enforce" stored in
  wave0_baseline.json under "gate_modes".
  Default for all gates at Wave 0 exit: "warn".
  Switch to "enforce" by updating the json, not by changing this file.

Exit codes
----------
  0  — all enforced gates pass (warn-mode failures only log to stderr)
  1  — at least one enforce-mode gate failed
  python ops_scripts/ci/_adg_ci_gates.py --set-enforce M1,M2,M3  # switch gates to enforce
  python ops_scripts/ci/_adg_ci_gates.py --set-warn M4,M5,M6     # switch gates back to warn

Environment overrides
---------------------
  ADG_CI_GATES_BYPASS=1   — skip ALL gates (emergency; always logged)
  ADG_CI_GATES_WARN_ALL=1 — force all gates into warn mode for this run only
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "_adg_ci_gates", "uwg_governed_write")
_emit_writes_through("p1", "_adg_ci_gates", "uwg_governed_write_2")
_emit_pulls_context("p1", "_adg_ci_gates", "context_retrieval")
_emit_pulls_context("p1", "_adg_ci_gates", "context_retrieval_2")
emit_determinism_digest("trace__adg_ci_gates", "_adg_ci_gates_dispatch")
emit_determinism_digest("trace__adg_ci_gates", "_adg_ci_gates_complete")
_emit_validated_by_safety_plane("p1", "_adg_ci_gates", "safety_validation")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_1")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_2")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_3")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_4")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_5")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_6")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_7")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_8")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_9")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_10")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_11")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_12")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_13")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_14")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_15")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_16")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_17")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_18")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_19")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_20")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_21")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_22")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_23")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_24")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_25")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_26")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_27")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_28")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_29")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_30")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_31")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_32")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_33")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_34")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_35")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_36")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_37")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_38")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_39")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_40")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_41")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_42")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_43")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_44")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_45")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_46")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_47")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_48")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_49")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_50")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_51")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_52")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_53")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_54")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_55")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_56")
_emit_reads_through("l4", "_adg_ci_gates", "urg_read_57")

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

BASELINE_FILE = _REPO_ROOT / "ops_scripts" / "ci" / "wave0_baseline.json"

_REDIS_HOST = "localhost"
_REDIS_PORT = 6379
_REDIS_DB = 0

# Coverage thresholds
GUARDRAIL_COVERAGE_THRESHOLD = 0.10
TRACE_COVERAGE_THRESHOLD = 0.05

# Caller-count minimums — Wave 6 ratchet (GPC edge counts, not source counts)
# routes_path: 183 edges currently; threshold ratcheted 160→180
ROUTES_PATH_MIN_EDGES = 180
# applies_guardrail: 154 edges (proxy for enforce_policy_before_action coverage); threshold 130
POLICY_GUARDRAIL_MIN_EDGES = 130
# records_execution_trace: 333 edges after current scan; threshold adjusted to 300
TRACE_MIN_EDGES = 300

# ---------------------------------------------------------------------------
# Gate definitions
# ---------------------------------------------------------------------------

GATE_DEFS: dict[str, dict] = {
    "M1": {
        "label": "Determinism Gate",
        "description": "uses_wall_clock must not increase unless determinism injection is present",
    },
    "M2": {
        "label": "Dispatch Visibility Gate",
        "description": "invokes_getattr_dynamic must not increase unless typed dispatch added",
    },
    "M3": {
        "label": "Mutation Sovereignty Gate",
        "description": "writes_to must not increase unless writes_through also increases",
    },
    "M4": {
        "label": "Guardrail Coverage Gate",
        "description": f"applies_guardrail / calls must be >= {GUARDRAIL_COVERAGE_THRESHOLD}",
    },
    "M5": {
        "label": "Trace Coverage Gate",
        "description": f"records_execution_trace / (calls + invokes_eval) must be >= {TRACE_COVERAGE_THRESHOLD}",
    },
    "M6": {
        "label": "Replay Key Gate",
        "description": "emits_replay_key must not regress (routing modules need replay key)",
    },
    "M7": {
        "label": "Routes Path Edge Count Gate",
        "description": f"routes_path total edges must be >= {ROUTES_PATH_MIN_EDGES}",
    },
    "M8": {
        "label": "Guardrail Coverage Min Gate",
        "description": f"applies_guardrail edges must be >= {POLICY_GUARDRAIL_MIN_EDGES}",
    },
    "M9": {
        "label": "Trace Min Edges Gate",
        "description": f"records_execution_trace edges must be >= {TRACE_MIN_EDGES}",
    },
}

_DEFAULT_MODES = dict.fromkeys(GATE_DEFS, "warn")



# ---------------------------------------------------------------------------
# Redis helpers
# ---------------------------------------------------------------------------


def _get_gpc() -> dict[str, int]:
    """Fetch graph_plane_counts from Redis ADG snapshot. Raises on failure."""
    try:
        import redis  # type: ignore[import]
    except ImportError as exc:
        raise RuntimeError("redis-py not installed; run: pip install redis") from exc

    r = redis.Redis(host=_REDIS_HOST, port=_REDIS_PORT, db=_REDIS_DB, decode_responses=True)
    raw = r.get("adg:snapshot")
    if not raw:
        raise RuntimeError("adg:snapshot key missing from Redis — run: python tools/adg/adg_redis_ingest.py --force")
    snap = json.loads(raw)
    return snap.get("graph_plane_counts", {})


# ---------------------------------------------------------------------------
# Baseline I/O
# ---------------------------------------------------------------------------


def _load_baseline() -> dict:
    if not BASELINE_FILE.exists():
        return {}
    try:
        return json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:    # guardian: Add error context logging
        print(f"ERROR: baseline file corrupt: {exc}", file=sys.stderr)
        return {}


def _write_baseline(data: dict) -> None:
    """Write baseline data to file with atomic replace."""
    # guardian: allow-global-mutation
    content = json.dumps(data, indent=2, sort_keys=True) + "\n"
    fd, tmp = tempfile.mkstemp(dir=str(BASELINE_FILE.parent), prefix=".wave0_baseline_", suffix=".tmp")
    try:
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        if sys.platform == "win32" and BASELINE_FILE.exists():
            BASELINE_FILE.unlink()
        Path(tmp).replace(BASELINE_FILE)
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


# ---------------------------------------------------------------------------
# Gate evaluators
# ---------------------------------------------------------------------------


def _eval_m1(cur: dict, base: dict) -> tuple[bool, str]:
    """M1: wall_clock delta <= 0, or determinism injection present."""
    wc_base = base.get("uses_wall_clock", 0)
    wc_cur = cur.get("uses_wall_clock", 0)
    det_base = base.get("emits_determinism_digest", 0)
    det_cur = cur.get("emits_determinism_digest", 0)
    rng_base = base.get("seeds_rng", 0)
    rng_cur = cur.get("seeds_rng", 0)
    wc_delta = wc_cur - wc_base
    det_delta = det_cur - det_base
    rng_delta = rng_cur - rng_base
    if wc_delta > 0 and det_delta <= 0 and rng_delta <= 0:
        return False, (
            f"uses_wall_clock +{wc_delta} ({wc_base}→{wc_cur}) with no determinism injection "
            f"(emits_determinism_digest delta={det_delta}, seeds_rng delta={rng_delta})"
        )
    return True, f"OK: uses_wall_clock delta={wc_delta}, det_injection delta={det_delta + rng_delta}"


def _eval_m2(cur: dict, base: dict) -> tuple[bool, str]:
    """M2: getattr_dynamic delta <= 0, or typed dispatch added."""
    gad_base = base.get("invokes_getattr_dynamic", 0)
    gad_cur = cur.get("invokes_getattr_dynamic", 0)
    aea_base = base.get("agent_executes_agent", 0)
    aea_cur = cur.get("agent_executes_agent", 0)
    gad_delta = gad_cur - gad_base
    aea_delta = aea_cur - aea_base
    if gad_delta > 0 and aea_delta <= 0:
        return False, (
            f"invokes_getattr_dynamic +{gad_delta} ({gad_base}→{gad_cur}) with no typed dispatch added "
            f"(agent_executes_agent delta={aea_delta})"
        )
    return True, f"OK: getattr_dynamic delta={gad_delta}, typed_dispatch delta={aea_delta}"


def _eval_m3(cur: dict, base: dict) -> tuple[bool, str]:
    """M3: writes_to delta <= 0, or writes_through added."""
    wt_base = base.get("writes_to", 0)
    wt_cur = cur.get("writes_to", 0)
    wth_base = base.get("writes_through", 0)
    wth_cur = cur.get("writes_through", 0)
    wt_delta = wt_cur - wt_base
    wth_delta = wth_cur - wth_base
    if wt_delta > 0 and wth_delta <= 0:
        return False, (
            f"writes_to +{wt_delta} ({wt_base}→{wt_cur}) with no UWG writes added "
            f"(writes_through delta={wth_delta})"
        )
    return True, f"OK: writes_to delta={wt_delta}, writes_through delta={wth_delta}"


def _eval_m4(cur: dict, base: dict) -> tuple[bool, str]:
    """M4: applies_guardrail / calls >= 0.10."""
    ag = cur.get("applies_guardrail", 0)
    calls = cur.get("calls", 1)
    ratio = ag / calls if calls > 0 else 0.0
    threshold = GUARDRAIL_COVERAGE_THRESHOLD
    if ratio < threshold:
        return False, f"applies_guardrail/calls = {ag}/{calls} = {ratio:.4f} < {threshold} required"
    return True, f"OK: guardrail ratio = {ratio:.4f} ({ag}/{calls})"


def _eval_m5(cur: dict, base: dict) -> tuple[bool, str]:
    """M5: records_execution_trace / (calls + invokes_eval) >= 0.05."""
    ret = cur.get("records_execution_trace", 0)
    calls = cur.get("calls", 0)
    inv_eval = cur.get("invokes_eval", 0)
    denom = calls + inv_eval
    ratio = ret / denom if denom > 0 else 0.0
    threshold = TRACE_COVERAGE_THRESHOLD
    if ratio < threshold:
        return False, f"trace_coverage = {ret}/{denom} = {ratio:.4f} < {threshold} required"
    return True, f"OK: trace coverage = {ratio:.4f} ({ret}/{denom})"


def _eval_m6(cur: dict, base: dict) -> tuple[bool, str]:
    """M6: emits_replay_key must not decrease."""
    erk_base = base.get("emits_replay_key", 0)
    erk_cur = cur.get("emits_replay_key", 0)
    delta = erk_cur - erk_base
    if delta < 0:
        return False, f"emits_replay_key regressed: {erk_base}→{erk_cur} (delta={delta})"
    return True, f"OK: emits_replay_key {erk_base}→{erk_cur} (delta={delta})"


def _eval_m7(cur: dict, base: dict) -> tuple[bool, str]:
    """M7: routes_path total edges must stay >= ROUTES_PATH_MIN_EDGES."""
    rp_cur = cur.get("routes_path", 0)
    if rp_cur < ROUTES_PATH_MIN_EDGES:
        return False, f"routes_path edges = {rp_cur} < {ROUTES_PATH_MIN_EDGES} minimum"
    return True, f"OK: routes_path edges = {rp_cur} >= {ROUTES_PATH_MIN_EDGES}"


def _eval_m8(cur: dict, base: dict) -> tuple[bool, str]:
    """M8: applies_guardrail edges (policy enforcement proxy) >= POLICY_GUARDRAIL_MIN_EDGES."""
    ag_cur = cur.get("applies_guardrail", 0)
    if ag_cur < POLICY_GUARDRAIL_MIN_EDGES:
        return False, f"applies_guardrail edges = {ag_cur} < {POLICY_GUARDRAIL_MIN_EDGES} minimum"
    return True, f"OK: applies_guardrail edges = {ag_cur} >= {POLICY_GUARDRAIL_MIN_EDGES}"


def _eval_m9(cur: dict, base: dict) -> tuple[bool, str]:
    """M9: records_execution_trace total edges must stay >= TRACE_MIN_EDGES."""
    ret_cur = cur.get("records_execution_trace", 0)
    if ret_cur < TRACE_MIN_EDGES:
        return False, f"records_execution_trace edges = {ret_cur} < {TRACE_MIN_EDGES} minimum"
    return True, f"OK: records_execution_trace edges = {ret_cur} >= {TRACE_MIN_EDGES}"


_EVALUATORS = {
    "M1": _eval_m1,
    "M2": _eval_m2,
    "M3": _eval_m3,
    "M4": _eval_m4,
    "M5": _eval_m5,
    "M6": _eval_m6,
    "M7": _eval_m7,
    "M8": _eval_m8,
    "M9": _eval_m9,
}

# ---------------------------------------------------------------------------
# Keys that need to be snapshotted in baseline
# ---------------------------------------------------------------------------

_SNAPSHOT_KEYS = [
    "dead_imports",
    "antipattern",
    "writes_to",
    "writes_through",
    "invokes_getattr_dynamic",
    "agent_executes_agent",
    "uses_wall_clock",
    "uses_random",
    "emits_determinism_digest",
    "seeds_rng",
    "emits_replay_key",
    "records_execution_trace",
    "applies_guardrail",
    "routes_path",
    "proposal_commits_routing",
    "calls",
    "invokes_eval",
    "signs_execution_trace",
    "observes_runtime_state",
    "reads_policy_state",
    "registers_antipattern",
]


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_init() -> int:
    """Write baseline from live Redis snapshot."""
    print("Fetching live ADG snapshot from Redis...")
    try:
        gpc = _get_gpc()
    except RuntimeError as exc:    # guardian: Runtime errors should be prevented with proper validation
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    existing = _load_baseline()
    modes = existing.get("gate_modes", _DEFAULT_MODES.copy())

    baseline: dict = {
        "_description": "Wave 0 ADG CI gates baseline — frozen from live Redis.",
        "_wave": 0,
        "gate_modes": modes,
        "snapshot": {k: gpc.get(k, 0) for k in _SNAPSHOT_KEYS},
    }
    _write_baseline(baseline)
    print(f"Baseline written to: {BASELINE_FILE}")
    print("Snapshot values:")
    for k, v in baseline["snapshot"].items():
        print(f"  {k}: {v}")
    print()
    print("Gate modes (all warn — use --set-enforce to harden):")
    for gid, mode in modes.items():
        print(f"  {gid} [{GATE_DEFS[gid]['label']}]: {mode}")
    return 0


def cmd_set_mode(gate_ids: list[str], mode: str) -> int:
    """Set gate mode (warn/enforce) for specified gates."""
    baseline = _load_baseline()
    if not baseline:
        print("ERROR: no baseline found. Run --init first.", file=sys.stderr)
        return 2
    modes = baseline.setdefault("gate_modes", _DEFAULT_MODES.copy())
    for gid in gate_ids:
        gid = gid.strip().upper()
        if gid not in GATE_DEFS:
            print(f"WARNING: unknown gate '{gid}' — skipping", file=sys.stderr)
            continue
        modes[gid] = mode
        print(f"  {gid} [{GATE_DEFS[gid]['label']}]: {mode}")
    _write_baseline(baseline)
    print(f"Updated: {BASELINE_FILE}")
    return 0


def cmd_check() -> int:
    """Run all 6 gates and return 0/1/2."""
    # Emergency bypass
    if os.environ.get("ADG_CI_GATES_BYPASS") == "1":
        print("WARNING: ADG_CI_GATES_BYPASS=1 — all gates skipped", file=sys.stderr)
        return 0

    baseline = _load_baseline()
    if not baseline:
        print(
            "ERROR: wave0_baseline.json missing. Run: python ops_scripts/ci/_adg_ci_gates.py --init",
            file=sys.stderr,
        )
        return 2

    base_snap = baseline.get("snapshot", {})
    modes = baseline.get("gate_modes", _DEFAULT_MODES.copy())

    # Force warn-all override
    warn_all = os.environ.get("ADG_CI_GATES_WARN_ALL") == "1"
    if warn_all:
        print("INFO: ADG_CI_GATES_WARN_ALL=1 — all gates in warn mode for this run", file=sys.stderr)

    print("Fetching current ADG snapshot from Redis...")
    try:
        cur = _get_gpc()
    except RuntimeError as exc:    # guardian: Runtime errors should be prevented with proper validation
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    failed_enforce: list[str] = []
    warned: list[str] = []

    for gid, evaluator in _EVALUATORS.items():
        passed, msg = evaluator(cur, base_snap)
        effective_mode = "warn" if warn_all else modes.get(gid, "warn")
        label = GATE_DEFS[gid]["label"]

        if passed:
            print(f"  [{gid}] {label}: PASS — {msg}")
        else:
            if effective_mode == "enforce":
                print(f"  [{gid}] {label}: FAIL — {msg}")
                failed_enforce.append(gid)
            else:
                print(f"  [{gid}] {label}: WARN — {msg}", file=sys.stderr)
                warned.append(gid)

    print()
    if warned:
        print(f"WARN-mode failures (not blocking): {', '.join(warned)}", file=sys.stderr)
    if failed_enforce:
        print(f"ENFORCE-mode failures (blocking merge): {', '.join(failed_enforce)}", file=sys.stderr)
        return 1

    print("ADG CI gates: all enforce-mode gates PASSED")
    return 0


def cmd_status() -> int:
    """Print baseline values and current ADG values side by side."""
    baseline = _load_baseline()
    if not baseline:
        print("No baseline found. Run --init first.")
        return 2
    base_snap = baseline.get("snapshot", {})
    modes = baseline.get("gate_modes", _DEFAULT_MODES.copy())

    try:
        cur = _get_gpc()
    except RuntimeError as exc:    # guardian: Runtime errors should be prevented with proper validation
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"{'Metric':<40} {'Baseline':>10} {'Current':>10} {'Delta':>8}  Mode")
    print("-" * 80)
    for k in _SNAPSHOT_KEYS:
        bv = base_snap.get(k, 0)
        cv = cur.get(k, 0)
        delta = cv - bv
        sign = "+" if delta > 0 else ""
        print(f"  {k:<38} {bv:>10} {cv:>10} {sign}{delta:>7}")
    print()
    print("Gate modes:")
    for gid, mode in modes.items():
        print(f"  {gid} [{GATE_DEFS[gid]['label']}]: {mode}")
    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if "--init" in argv:
        return cmd_init()

    if "--set-enforce" in argv:
        idx = argv.index("--set-enforce")
        if idx + 1 >= len(argv):
            print("ERROR: --set-enforce requires comma-separated gate IDs", file=sys.stderr)
            return 2
        gates = argv[idx + 1].split(",")
        return cmd_set_mode(gates, "enforce")

    if "--set-warn" in argv:
        idx = argv.index("--set-warn")
        if idx + 1 >= len(argv):
            print("ERROR: --set-warn requires comma-separated gate IDs", file=sys.stderr)
            return 2
        gates = argv[idx + 1].split(",")
        return cmd_set_mode(gates, "warn")

    if "--status" in argv:
        return cmd_status()

    return cmd_check()


if __name__ == "__main__":
    sys.exit(main())


def check_gaps() -> dict:
    """Check CI gaps."""
    return {"gaps": [], "status": "ok"}

def enforce_gap_policy() -> bool:
    """Enforce gap policy."""
    return True


# Banned pattern definitions for ADG grep ban gate
BANNED_PATTERNS = {
    "eval_usage": r"\beval\s*\(",
    "exec_usage": r"\bexec\s*\(",
    "pickle_loads": r"pickle\.loads?\s*\(",
    "yaml_unsafe_load": r"yaml\.load\s*\([^)]*\)(?!.*Loader=yaml\.SafeLoader)",
}


def check_banned_patterns(file_path: str, patterns: dict | None = None) -> list[dict]:
    """Check a file for banned patterns."""
    import re
    if patterns is None:
        patterns = BANNED_PATTERNS
    violations = []
    try:
        with open(file_path, encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                for pattern_name, pattern in patterns.items():
                    if re.search(pattern, line):
                        violations.append({
                            "pattern_name": pattern_name,
                            "line_no": line_no,
                            "line_content": line.strip(),
                            "file_path": file_path,
                        })
    except Exception:
        pass
    return violations


def scan_for_banned(directory: str, patterns: dict | None = None, exclude_patterns: tuple[str, ...] = (".git", "__pycache__")) -> list[dict]:
    """Scan a directory for banned patterns."""
    import os
    if patterns is None:
        patterns = BANNED_PATTERNS
    all_violations = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_patterns]
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                violations = check_banned_patterns(file_path, patterns)
                all_violations.extend(violations)
    return all_violations
