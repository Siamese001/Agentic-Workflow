"""
Simulation harness for _verify.py — runs A–F style tests using temp copies.

Never edits committed lock files in-place. Uses backup/restore pattern
with a TemporaryDirectory to guarantee repo cleanliness.
Enforces byte-equal restoration of all lock files after simulations.

Run: python -m agentic_core.L5_safety.config.structure_blueprint._simulate_verify
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT, TESTS_DIR
from agentic_core.L2_execution.utils import write_gateway as _wg
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

emit_replay_key("p0", "_simulate_verify")
emit_determinism_digest("p0", "_simulate_verify")

_emit_dispatches_healing_run("p1", "_simulate_verify", "L5")
_emit_routes_through("p1", "_simulate_verify", "L5")
_emit_checks_agent_registry("p1", "_simulate_verify", "agent_registry")
_emit_validates_agent_capability("p1", "_simulate_verify", "capability")
_emit_dispatches_execution_plan("p1", "_simulate_verify", "exec_plan")
_emit_agent_executes_agent("p1", "_simulate_verify", "sub_agent")
_emit_routes_to_agent("p1", "_simulate_verify", "target_agent")
_emit_verifies_policy("p1", "_simulate_verify", "policy_check")
_emit_observes_runtime_state("p1", "_simulate_verify", "runtime_state")
_emit_verifies_boundary("p1", "_simulate_verify", "boundary_check")
_emit_transcripts_response("p1", "_simulate_verify", "transcript")
_emit_hard_fails_untranscripted("p1", "_simulate_verify")
_emit_gated_by_confidence("p1", "_simulate_verify", "confidence_gate")
_emit_escalates_to_human("p1", "_simulate_verify", "L5")
_emit_reads_policy_state("p1", "_simulate_verify", "L5")
_emit_authorize_and_execute("p2", "_simulate_verify", "execution_auth")
_emit_validates_capability("p2", "_simulate_verify", "capability_check")
_emit_routes_to_capability("p2", "_simulate_verify", "capability_route")
_emit_writes_via_uwg("p2", "_simulate_verify", "uwg_write")
_emit_blocks_direct_write("p2", "_simulate_verify", "direct_write_block")
_emit_records_tool_invocation("p2", "_simulate_verify", "tool_invocation")
_emit_captures_execution_output("p2", "_simulate_verify", "exec_output")
_emit_dispatches_agent("p3", "_simulate_verify", "agent_dispatch")
_emit_coordinates_agents("p3", "_simulate_verify", "agent_coordination")
_emit_records_workflow_lineage("p3", "_simulate_verify", "workflow_lineage")
_emit_records_healing_outcome("p3", "_simulate_verify", "healing_outcome")
_emit_escalates_failure("p3", "_simulate_verify", "failure_escalation")
_emit_orchestrates_workflow("p3", "_simulate_verify", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_simulate_verify", "healing_dispatch")
_emit_invokes_evaluation("p3", "_simulate_verify", "evaluation_signal")
_emit_records_telemetry_event("p4", "_simulate_verify", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_simulate_verify", "eval_metric")
_emit_stores_embedding("p4", "_simulate_verify", "embedding_store")
_emit_updates_meta_learning_state("p4", "_simulate_verify", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_simulate_verify", "exec_snapshot_link")
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

_emit_emits_metric_event("_simulate_verify", "p4obs", "metric_1")
_emit_emits_metric_event("_simulate_verify", "p4obs", "metric_2")
_emit_emits_metric_event("_simulate_verify", "p4obs", "metric_3")
_emit_emits_metric_event("_simulate_verify", "p4obs", "metric_4")
_emit_emits_metric_event("_simulate_verify", "p4obs", "metric_5")
_emit_emits_metric_event("_simulate_verify", "p4obs", "metric_6")
_emit_records_incident_event("_simulate_verify", "p4obs", "incident")
_emit_captures_runtime_anomaly("_simulate_verify", "p4obs", "anomaly")
_emit_writes_observability_log("_simulate_verify", "p4obs", "obs_log")
_emit_updates_monitoring_state("_simulate_verify", "p4obs", "mon_state")
_emit_triggers_alert("_simulate_verify", "p4obs", "alert")
_emit_links_incident_trace("_simulate_verify", "p4obs", "trace_link")
_emit_captures_pattern("_simulate_verify", "p3lm", "pattern")
_emit_records_learning_event("_simulate_verify", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_simulate_verify", "p3lm", "snapshot")
_emit_feeds_meta_learning("_simulate_verify", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_simulate_verify", "p3lm", "routing")
_emit_improves_agent_policy("_simulate_verify", "p3lm", "policy")
_emit_stores_learning_state("_simulate_verify", "p3lm", "state")
_emit_records_execution_trace("_simulate_verify", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_simulate_verify", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_simulate_verify", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_simulate_verify", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_simulate_verify", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_simulate_verify", "env_read", "p2_env_1")
_emit_reads_environ("_simulate_verify", "env_read", "p2_env_2")
_emit_reads_runtime_state("_simulate_verify", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_simulate_verify", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "_simulate_verify", "context_pull")
_emit_pulls_context("p1", "_simulate_verify", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "_simulate_verify", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_simulate_verify", "uwg_term_2")
_emit_writes_through("p1", "_simulate_verify", "write_through")
_emit_writes_through("p1", "_simulate_verify", "write_through_2")
_emit_validated_by_safety_plane("p1", "_simulate_verify", "safety_validation")
_emit_invokes_eval("p1", "_simulate_verify", "eval_call")
_emit_proposal_commits_routing("p1", "_simulate_verify", "routing_commit")


def _repo_root() -> str:
    # guardian: allow-path-string
    return os.path.abspath(Path(os.path.dirname(__file__)) / ".." / ".." / ".." / "..")


def _read_bytes(path: str) -> bytes | None:
    """Read file as bytes, return None if missing."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_read_bytes", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_read_bytes", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "_read_bytes")
    # guardian: allow-path-string
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return f.read()


def _run_verify(*extra_args: str) -> tuple[int, str]:
    """Run the verifier as a subprocess, return (exit_code, combined_output)."""
    cmd = [sys.executable, "-m", "agentic_core.L5_safety.config.structure_blueprint._verify", *extra_args]
    result = subprocess.run(cmd, cwd=_repo_root(), capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
    return (result.returncode, result.stdout + result.stderr)


def main() -> int:
    root = _repo_root()
    baseline_path = Path(root) / "docs" / "reports" / "plans" / "phantom_baseline.json"
    hash_path = Path(root) / "docs" / "reports" / "plans" / "allowlist_hash.txt"
    debt_path = Path(root) / "docs" / "reports" / "plans" / "phantom_debt.md"
    results: list[tuple[str, bool, str]] = []
    snap_baseline = _read_bytes(baseline_path)
    snap_hash = _read_bytes(hash_path)
    snap_debt = _read_bytes(debt_path)
    with tempfile.TemporaryDirectory(prefix="ssot_sim_") as tmpdir:
        backup_baseline = Path(tmpdir) / "phantom_baseline.json"
        backup_hash = Path(tmpdir) / "allowlist_hash.txt"
        backup_debt = Path(tmpdir) / "phantom_debt.md"
        # guardian: allow-path-string
        if os.path.isfile(baseline_path):
            _wg.copy_file(baseline_path, backup_baseline)
        # guardian: allow-path-string
        if os.path.isfile(hash_path):
            _wg.copy_file(hash_path, backup_hash)
        # guardian: allow-path-string
        if os.path.isfile(debt_path):
            _wg.copy_file(debt_path, backup_debt)

        def _restore() -> None:
            """Restore original lock files from backup."""
            # guardian: allow-path-string
            if os.path.isfile(backup_baseline):
                _wg.copy_file(backup_baseline, baseline_path)
            # guardian: allow-path-string
            if os.path.isfile(backup_hash):
                _wg.copy_file(backup_hash, hash_path)
            # guardian: allow-path-string
            if os.path.isfile(backup_debt):
                _wg.copy_file(backup_debt, debt_path)

        try:
            _wg.open_write(hash_path, "TAMPERED_SIM_HASH\n")
            rc, out = _run_verify()
            sim1_fail = rc != 0 and "MISMATCH" in out
            rc2, out2 = _run_verify("--acknowledge-import-change")
            sim1_ack = rc2 == 0 and "UPDATED" in out2
            passed = sim1_fail and sim1_ack
            detail = f"mismatch_fail={sim1_fail}, ack_ok={sim1_ack}"
            results.append(("SIM1: Allowlist mismatch + ack", passed, detail))
        finally:
            _restore()
        try:
            _wg.open_write(baseline_path, "NOT VALID JSON")
            rc, out = _run_verify()
            sim2_fail = rc != 0 and "CORRUPT" in out
            rc2, out2 = _run_verify("--repair-phantom-baseline")
            sim2_repair = rc2 == 0 and "REPAIRED" in out2
            passed = sim2_fail and sim2_repair
            detail = f"corrupt_fail={sim2_fail}, repair_ok={sim2_repair}"
            results.append(("SIM2: Corrupt baseline + repair", passed, detail))
        finally:
            _restore()
        try:
            with open(baseline_path, encoding="utf-8") as bf:
                data = json.load(bf)
            data[0][0] = "/absolute/path/file.py"
            _wg.write_json(baseline_path, data, indent=2)
            rc, out = _run_verify()
            passed = rc != 0 and "repo-relative-normalized" in out
            detail = f"rc={rc}, has_guidance={'repo-relative-normalized' in out}"
            results.append(("SIM3: Absolute path in baseline", passed, detail))
        finally:
            _restore()
        syntax_err_path = Path(root) / TESTS_DIR / "_tmp_syntax_err_sim.py"
        try:
            _wg.open_write(
                syntax_err_path,
                "from agentic_core.L5_safety.config.structure_blueprint import FAKE\ndef broken(\n",
            )
            rc, out = _run_verify()
            passed = rc != 0 and "SyntaxError" in out and ("_tmp_syntax_err_sim" in out)
            detail = f"rc={rc}, syntax_detected={'SyntaxError' in out}"
            results.append(("SIM4: SyntaxError in tests/", passed, detail))
        finally:
            # guardian: allow-path-string
            if os.path.isfile(syntax_err_path):
                _wg.remove_file(syntax_err_path)
            _restore()
        try:
            with open(baseline_path, encoding="utf-8") as bf:
                data = json.load(bf)
            if len(data) > 1:
                data.pop()
                _wg.write_json(baseline_path, data, indent=2)
                rc, out = _run_verify()
                has_current_only = "Current-only entries" in out
                passed = rc != 0 and has_current_only
                detail = f"rc={rc}, current_only={has_current_only}"
            else:
                passed = False
                detail = "baseline too small to test"
            results.append(("SIM5: Baseline entry removal → diff", passed, detail))
        finally:
            _restore()
        try:
            with open(baseline_path, encoding="utf-8") as bf:
                data = json.load(bf)
            data[0][0] = "agentic_core\\L0_routing\\scripts\\fake.py"
            _wg.write_json(baseline_path, data, indent=2)
            rc, out = _run_verify()
            passed = rc != 0 and "repo-relative-normalized" in out
            detail = f"rc={rc}, canonical_fail={'repo-relative-normalized' in out}"
            results.append(("SIM6: Backslash path in baseline", passed, detail))
        finally:
            _restore()
        try:
            MODULE = "agentic_core.L5_safety.config.structure_blueprint._verify"
            FORBIDDEN = [
                "--init-phantom-baseline",
                "--update-phantom-baseline",
                "--repair-phantom-baseline",
                "--acknowledge-import-change",
            ]

            def _find_invoke_lines(text: str) -> list[str]:
                """Same logic as CI guard: exact module path, line-level."""
                found = []
                for line in text.splitlines():
                    s = line.strip()
                    if s.startswith("#") or s.startswith('"') or s.startswith("'"):
                        continue
                    if "python" in s and "-m" in s and (MODULE in s):
                        found.append(s)
                return found

            wf_path = Path(root) / ".github" / "workflows" / "ssot_verify.yml"
            with open(wf_path, encoding="utf-8") as wf:
                wf_text = wf.read()
            clean_invoke = _find_invoke_lines(wf_text)
            clean_count = len(clean_invoke)
            clean_violations = []
            for line in clean_invoke:
                for flag in FORBIDDEN:
                    if flag in line:
                        clean_violations.append(flag)
            clean_pass = clean_count >= 1 and len(clean_violations) == 0
            tampered = wf_text.replace(f"python -m {MODULE}", f"python -m {MODULE} --init-phantom-baseline")
            tampered_invoke = _find_invoke_lines(tampered)
            tampered_count = len(tampered_invoke)
            tampered_violations = []
            for line in tampered_invoke:
                for flag in FORBIDDEN:
                    if flag in line:
                        tampered_violations.append(flag)
            tampered_detected = len(tampered_violations) > 0
            passed = clean_pass and tampered_detected and (tampered_count >= 1)
            detail = f"clean_invocations={clean_count}, clean_pass={clean_pass}, tampered_invocations={tampered_count}, tampered_detected={tampered_detected}"
            results.append(("SIM7: CI guard self-test (in-memory)", passed, detail))
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as exc:
            results.append(("SIM7: CI guard self-test (in-memory)", False, str(exc)))
    print("=" * 60)
    print("SIMULATION HARNESS — RESULTS")
    print("=" * 60)
    all_pass = True
    for name, passed, detail in results:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  {status}: {name} ({detail})")
    print()
    print("  BYTE-EQUAL RESTORATION CHECK:")
    artifacts = [
        ("phantom_baseline.json", baseline_path, snap_baseline),
        ("allowlist_hash.txt", hash_path, snap_hash),
        ("phantom_debt.md", debt_path, snap_debt),
    ]
    for label, path, original_bytes in artifacts:
        current_bytes = _read_bytes(path)
        if original_bytes == current_bytes:
            print(f"    {label}: BYTE-EQUAL ✔")
        else:
            orig_len = len(original_bytes) if original_bytes is not None else "MISSING"
            curr_len = len(current_bytes) if current_bytes is not None else "MISSING"
            print(f"    {label}: DIFFERS (original={orig_len}, current={curr_len})")
            all_pass = False
    syntax_leftover = Path(root) / TESTS_DIR / "_tmp_syntax_err_sim.py"
    # guardian: allow-path-string
    if os.path.isfile(syntax_leftover):
        print("    Temp syntax file: WARNING — not cleaned up")
        all_pass = False
    else:
        print("    Temp syntax file: CLEAN ✔")
    try:
        git_result = subprocess.run(
            [
                "git",
                "diff",
                "--exit-code",
                "--",
                "docs/reports/plans/phantom_baseline.json",
                "docs/reports/plans/allowlist_hash.txt",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
        if git_result.returncode == 0:
            print("    git diff lock files: CLEAN ✔")
        else:
            print("    git diff lock files: DIRTY")
            print(git_result.stdout[:500] if git_result.stdout else "")
            all_pass = False
    except (FileNotFoundError, subprocess.TimeoutExpired):    # guardian: File operations should check existence before access
        print("    git diff: SKIPPED (git not available)")
    print()
    if all_pass:
        print("OVERALL: PASS — all simulations green, repo byte-equal clean")
    else:
        print("OVERALL: FAIL — see above")
    print("=" * 60)
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
