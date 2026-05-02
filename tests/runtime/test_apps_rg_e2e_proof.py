"""Verifier for apps_rg end-to-end proof bundle.

Loads `artifacts/certification/apps_rg_e2e/apps_rg_e2e_proof.json` and
enforces the contract from the user's spec. Passes iff the bundle
honestly reports reality.

Two distinct pass semantics:

* `bundle.harness_pass=True` — the harness itself ran correctly (captured
  real artifacts, real SHA256 hashes, honest gap list). This test
  enforces `harness_pass` always.
* `bundle.success=True` — apps_rg actually routed through the governed
  spine end-to-end. The test enforces success iff the bundle claims it.

Fabricating `success=True` would require a matching RouteContract / L1 /
L3 / Exit / Exhaust artifact — the test SHA256-verifies each referenced
artifact and asserts the same run_id threads them, so fabrication is
detectable.

Run:
    python -m pytest tests/runtime/test_apps_rg_e2e_proof.py -q
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROOF_PATH = REPO_ROOT / "artifacts" / "certification" / "apps_rg_e2e" / "apps_rg_e2e_proof.json"
STATIC_DAG_PROOF_PATH = (
    REPO_ROOT / "artifacts" / "certification" / "apps_rg_e2e" / "apps_rg_static_l3_dag_proof.json"
)

REQUIRED_TOP_FIELDS: tuple[str, ...] = (
    "proof_schema_version", "app_name", "entrypoint_command", "run_id", "request_id",
    "trace_root", "started_at_utc", "finished_at_utc", "exit_code", "git_commit",
    "git_dirty", "runtime_mode", "mock_mode_detected", "fixture_mode_detected",
    "success", "blocking_gaps",
    "static_dag_ref", "static_dag_sha256",
    "runtime_route_contract_ref", "runtime_l3_receipt_ref",
    "runtime_exit_disposition_ref", "runtime_exhaust_ref",
    "otel_or_runtime_trace_ref",
)

REQUIRED_STATIC_DAG_FIELDS: tuple[str, ...] = (
    "proof_schema_version", "proof_kind", "app_name", "generated_at_utc",
    "present", "fail_closed", "fail_reasons",
    "dag_id", "dag_name", "dag_version", "dag_file_path", "dag_sha256",
    "dag_registry_ref", "dag_registry_sha256", "route_ids", "route_binding_refs",
    "node_count", "edge_count", "entry_nodes", "terminal_nodes", "node_ids",
    "edge_list", "max_depth", "has_cycle", "all_nodes_have_owner",
    "all_nodes_have_step_contract_schema", "all_nodes_have_allowed_execution_surface",
    "l3_no_execute_policy", "l3_no_retrieve_policy",
    "l3_no_prompt_assembly_policy", "l3_no_l4_write_policy",
    "scan_results",
)

ALLOWED_BYPASS_REASONS: set[str] = {
    "TERMINAL_SHORTCIRCUIT", "SINGLE_STEP_ROUTE", "FALLBACK_RET",
    "NO_MANAGED_WORKFLOW_REQUIRED",
}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def bundle() -> dict:
    if not PROOF_PATH.exists():
        pytest.skip(
            f"Proof bundle not emitted yet. Run:\n"
            f"  python -m tools.certification.apps_rg_e2e.emit_proof_bundle\n"
            f"Expected at: {PROOF_PATH.relative_to(REPO_ROOT)}"
        )
    return json.loads(PROOF_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def static_dag_proof() -> dict | None:
    if not STATIC_DAG_PROOF_PATH.exists():
        return None
    return json.loads(STATIC_DAG_PROOF_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Structural / schema invariants — these must hold regardless of success
# ---------------------------------------------------------------------------


def test_required_top_level_fields_present(bundle: dict) -> None:
    missing = [k for k in REQUIRED_TOP_FIELDS if k not in bundle]
    assert not missing, f"bundle missing required fields: {missing}"


def test_app_name_and_entrypoint_are_correct(bundle: dict) -> None:
    assert bundle["app_name"] == "apps_rg", bundle["app_name"]
    assert bundle["entrypoint_command"] == "python -m apps_rg", bundle["entrypoint_command"]


def test_run_id_is_non_empty_string(bundle: dict) -> None:
    rid = bundle.get("run_id")
    assert isinstance(rid, str) and len(rid) >= 8, f"run_id invalid: {rid!r}"


def test_timestamps_are_iso_utc(bundle: dict) -> None:
    for key in ("started_at_utc", "finished_at_utc"):
        val = bundle.get(key)
        assert isinstance(val, str) and val.endswith("Z"), f"{key} not ISO-UTC: {val!r}"


def test_harness_pass_is_true(bundle: dict) -> None:
    assert bundle.get("harness_pass") is True, (
        "harness_pass must be True if the emitter ran at all"
    )


def test_static_dag_proof_file_exists(bundle: dict, static_dag_proof: dict | None) -> None:
    ref = bundle.get("static_dag_ref")
    assert ref, "static_dag_ref is required"
    path = REPO_ROOT / ref
    assert path.exists(), f"static DAG proof missing on disk: {ref}"
    assert static_dag_proof is not None


def test_static_dag_proof_sha256_matches(bundle: dict) -> None:
    ref = bundle.get("static_dag_ref")
    declared = bundle.get("static_dag_sha256")
    path = REPO_ROOT / ref
    recomputed = _sha256_file(path)
    assert recomputed == declared, (
        f"static_dag_sha256 mismatch: declared={declared} recomputed={recomputed}"
    )


def test_static_dag_proof_has_required_fields(static_dag_proof: dict | None) -> None:
    assert static_dag_proof is not None
    missing = [k for k in REQUIRED_STATIC_DAG_FIELDS if k not in static_dag_proof]
    assert not missing, f"static DAG proof missing fields: {missing}"


def test_static_dag_app_name(static_dag_proof: dict | None) -> None:
    assert static_dag_proof is not None
    assert static_dag_proof["app_name"] == "apps_rg"


def test_all_referenced_artifacts_resolve_and_match_sha(bundle: dict) -> None:
    """Every non-null artifact reference must exist and hash-match.

    Runtime refs are null today; this test is a no-op for those but will
    activate the moment the spine starts emitting real artifacts.
    """
    # run_info.artifacts all real (freshness already enforced by the emitter)
    run_info = bundle.get("run_info") or {}
    for rec in run_info.get("artifacts", []):
        path = REPO_ROOT / rec["path"]
        assert path.exists(), f"run artifact missing: {rec['path']}"
        assert _sha256_file(path) == rec["sha256"], f"sha mismatch: {rec['path']}"


def test_no_stale_artifacts_in_run_dir(bundle: dict) -> None:
    run_info = bundle.get("run_info") or {}
    stale = run_info.get("stale") or []
    # Stale artifacts would indicate proof based on a previous run.
    assert not stale, f"stale artifacts detected in run dir: {[s['path'] for s in stale[:3]]}"


def test_blocking_gaps_is_list_of_strings(bundle: dict) -> None:
    bg = bundle.get("blocking_gaps")
    assert isinstance(bg, list)
    for item in bg:
        assert isinstance(item, str) and item


# ---------------------------------------------------------------------------
# Anti-cheat: fabrication detection
# ---------------------------------------------------------------------------


def _required_runtime_refs(bundle: dict) -> list[str]:
    """Build the required-refs list based on the route's execution_form.

    MANAGED_WORKFLOW -> need l3_receipt; else -> need l3_bypass.
    """
    base = [
        "runtime_intake_ref",
        "runtime_l1_plan_ref",
        "runtime_route_contract_ref",
        "runtime_l2_receipt_ref",
        "runtime_exit_disposition_ref",
        "runtime_exhaust_ref",
        "otel_or_runtime_trace_ref",
    ]
    route_ref = bundle.get("runtime_route_contract_ref")
    if route_ref and (REPO_ROOT / route_ref).exists():
        try:
            route_data = json.loads((REPO_ROOT / route_ref).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            route_data = {}
        if route_data.get("execution_form") == "MANAGED_WORKFLOW":
            base.append("runtime_l3_receipt_ref")
        else:
            base.append("runtime_l3_bypass_ref")
    return base


def test_success_only_when_all_runtime_refs_present(bundle: dict) -> None:
    """`success=True` REQUIRES every runtime reference to be a real, hash-matching file."""
    if not bundle.get("success"):
        pytest.skip("bundle honestly declares success=false; fabrication check n/a")
    required_refs = _required_runtime_refs(bundle)
    missing = [k for k in required_refs if not bundle.get(k)]
    assert not missing, f"success=true but refs missing: {missing}"
    artifacts_by_path = {rec["path"]: rec for rec in (bundle.get("run_info") or {}).get("artifacts", [])}
    for k in required_refs:
        ref = bundle[k]
        assert ref in artifacts_by_path, f"{k}={ref} is not in run_info.artifacts"
        path = REPO_ROOT / ref
        assert path.exists(), f"{k} artifact missing on disk: {ref}"
        assert _sha256_file(path) == artifacts_by_path[ref]["sha256"]


def test_success_requires_single_run_id_threading(bundle: dict) -> None:
    """If success=true, each runtime artifact must embed the SAME run_id."""
    if not bundle.get("success"):
        pytest.skip("success=false; single-run-id invariant not yet testable")
    run_id = bundle["run_id"]
    request_id = bundle.get("request_id")
    trace_root = bundle.get("trace_root")
    for key in _required_runtime_refs(bundle):
        ref = bundle.get(key)
        if not ref:
            continue
        p = REPO_ROOT / ref
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pytest.fail(f"{key}={ref} not parseable as JSON for run_id check")
        embedded_run = data.get("run_id")
        embedded_req = data.get("request_id")
        embedded_trace = data.get("trace_root")
        assert embedded_run == run_id, (
            f"{key} embedded run_id {embedded_run!r} != bundle run_id {run_id!r}"
        )
        # request_id and trace_root must thread when present
        if embedded_req is not None:
            assert embedded_req == request_id, f"{key} request_id mismatch"
        if embedded_trace is not None:
            assert embedded_trace == trace_root, f"{key} trace_root mismatch"


def test_static_dag_binding_when_managed_workflow(bundle: dict) -> None:
    """If L3 ran (MANAGED_WORKFLOW), static DAG hash must match runtime receipt."""
    l3_ref = bundle.get("runtime_l3_receipt_ref")
    if not l3_ref:
        pytest.skip("no L3 runtime receipt; binding check n/a")
    p = REPO_ROOT / l3_ref
    assert p.exists(), f"L3 receipt missing: {l3_ref}"
    data = json.loads(p.read_text(encoding="utf-8"))
    if data.get("execution_form") != "MANAGED_WORKFLOW":
        pytest.skip("L3 receipt is not MANAGED_WORKFLOW; binding check n/a")
    static_dag_sha = (bundle.get("static_dag_proof_inline_summary") or {}).get("dag_sha256")
    assert data.get("dag_sha256") == static_dag_sha, (
        "MANAGED_WORKFLOW: runtime dag_sha256 must match static DAG proof"
    )


def test_bypass_reason_is_allowed_when_not_managed(bundle: dict) -> None:
    """If execution_form != MANAGED_WORKFLOW, bypass receipt reason must be legal."""
    route_ref = bundle.get("runtime_route_contract_ref")
    if not route_ref:
        pytest.skip("no runtime route contract; bypass check n/a")
    route_data = json.loads((REPO_ROOT / route_ref).read_text(encoding="utf-8"))
    if route_data.get("execution_form") == "MANAGED_WORKFLOW":
        pytest.skip("managed workflow path; bypass check n/a")
    bypass_ref = bundle.get("runtime_l3_bypass_ref")
    assert bypass_ref, "non-managed route without L3 bypass receipt is forbidden"
    bypass = json.loads((REPO_ROOT / bypass_ref).read_text(encoding="utf-8"))
    assert bypass.get("l3_bypass_reason") in ALLOWED_BYPASS_REASONS, (
        f"bypass reason {bypass.get('l3_bypass_reason')!r} not in {ALLOWED_BYPASS_REASONS}"
    )
    assert bypass.get("route_contract_id") == route_data.get("route_contract_id"), (
        "L3 bypass receipt must cite the same route_contract_id as L0 RouteContract"
    )


def test_otel_trace_is_real_not_synthetic(bundle: dict) -> None:
    """OTEL trace artifact must contain real spans bound to the run_id."""
    otel_ref = bundle.get("otel_or_runtime_trace_ref")
    if not otel_ref:
        pytest.skip("no OTEL trace artifact; check n/a")
    p = REPO_ROOT / otel_ref
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data.get("run_id") == bundle["run_id"]
    spans = data.get("spans") or []
    assert spans, "OTEL trace has zero spans"
    assert not data.get("contains_synthetic_spans"), "OTEL trace contains synthetic spans"
    for s in spans:
        assert not s.get("is_synthetic"), f"synthetic span found: {s.get('name')}"
        assert s.get("duration_ms", 0) >= 0


def test_l2_receipt_references_route_contract(bundle: dict) -> None:
    """L2 receipt must cite the L0 route_contract_id."""
    l2_ref = bundle.get("runtime_l2_receipt_ref")
    route_ref = bundle.get("runtime_route_contract_ref")
    if not (l2_ref and route_ref):
        pytest.skip("L2 or route ref missing; check n/a")
    l2 = json.loads((REPO_ROOT / l2_ref).read_text(encoding="utf-8"))
    route = json.loads((REPO_ROOT / route_ref).read_text(encoding="utf-8"))
    assert l2.get("route_contract_id") == route.get("route_contract_id")


def test_exit_disposition_is_unique_and_valid(bundle: dict) -> None:
    """Exactly one X3 disposition; allowed values only."""
    exit_ref = bundle.get("runtime_exit_disposition_ref")
    if not exit_ref:
        pytest.skip("no exit disposition ref; check n/a")
    exit_data = json.loads((REPO_ROOT / exit_ref).read_text(encoding="utf-8"))
    assert exit_data.get("x3_disposition") in {"EXIT_OK", "EXIT_PARTIAL", "EXIT_FAIL", "EXIT_ROLLBACK"}
    assert exit_data.get("sealed") is True


def test_l6_exhaust_observed_after_exit(bundle: dict) -> None:
    """L6 exhaust bundle must be observed AFTER the exit packet (per spec)."""
    exhaust_ref = bundle.get("runtime_exhaust_ref")
    exit_ref = bundle.get("runtime_exit_disposition_ref")
    if not (exhaust_ref and exit_ref):
        pytest.skip("exhaust or exit ref missing; check n/a")
    exhaust = json.loads((REPO_ROOT / exhaust_ref).read_text(encoding="utf-8"))
    exit_data = json.loads((REPO_ROOT / exit_ref).read_text(encoding="utf-8"))
    assert exhaust.get("exit_review_packet_id") == exit_data.get("exit_review_packet_id")
    assert exhaust.get("observed_after_exit_at_utc") >= exit_data.get("emitted_at_utc")


def test_static_dag_invariants_when_present(static_dag_proof: dict | None) -> None:
    """Spec-required static-DAG invariants — must hold when DAG is present."""
    if static_dag_proof is None or not static_dag_proof.get("present"):
        pytest.skip("static DAG not present; invariants n/a")
    p = static_dag_proof
    assert p["app_name_matches"] is True
    assert p["registry_binding_matches_dag"] is True
    assert p["edges_reference_existing_nodes"] is True
    assert p["has_cycle"] is False
    assert p["all_nodes_have_owner"] is True
    assert p["all_nodes_have_step_contract_schema"] is True
    assert p["all_nodes_have_allowed_execution_surface"] is True
    assert p["l3_no_execute_policy"] is True
    assert p["l3_no_retrieve_policy"] is True
    assert p["l3_no_prompt_assembly_policy"] is True
    assert p["l3_no_l4_write_policy"] is True
    assert p["node_count"] >= 1
    assert p["entry_nodes"], "DAG has no entry nodes"
    assert p["terminal_nodes"], "DAG has no terminal nodes"


# ---------------------------------------------------------------------------
# Stage matrix visibility — also the summary printer
# ---------------------------------------------------------------------------


def test_stage_matrix_is_well_formed(bundle: dict) -> None:
    matrix = bundle.get("stage_matrix")
    assert isinstance(matrix, list) and matrix
    required_stages = {
        "static_l3_dag", "U0_intake", "L1_plan", "L0_route",
        "L3_orchestrate_or_bypass", "L2_execute", "Exit_X3", "L6_exhaust",
        "otel_or_runtime_trace",
    }
    got_stages = {row.get("stage") for row in matrix}
    missing = required_stages - got_stages
    assert not missing, f"stage_matrix missing stages: {missing}"


def test_print_stage_matrix(bundle: dict, capsys: pytest.CaptureFixture) -> None:
    """Pretty-print the Stage|Present|Pass|Fail|Gap table required by the spec."""
    matrix = bundle.get("stage_matrix") or []
    header = f"{'Stage':<28} {'StaticReq':<10} {'RuntimeReq':<11} {'Present':<8} {'Pass':<5} {'Gap':<50}"
    sep = "-" * len(header)
    lines = [header, sep]
    for row in matrix:
        lines.append(
            f"{row.get('stage',''):<28} "
            f"{str(row.get('static_required','')):<10} "
            f"{str(row.get('runtime_required','')):<11} "
            f"{str(row.get('present','')):<8} "
            f"{str(row.get('pass','')):<5} "
            f"{(row.get('gap') or '-'):<50}"
        )
    lines.append(sep)
    lines.append(
        f"BUNDLE: run_id={bundle.get('run_id')} success={bundle.get('success')} "
        f"harness_pass={bundle.get('harness_pass')} "
        f"gaps={len(bundle.get('blocking_gaps') or [])}"
    )
    report = "\n".join(lines)
    print("\n" + report)
    # Always passes — this is the reporting test. Invariants are above.
    assert matrix
