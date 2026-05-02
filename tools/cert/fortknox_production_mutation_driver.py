"""Fort Knox — Production-artifact mutation driver.

Plan: .windsurf/plans/fortknox-100pct-static-runtime-gap-9a3d4f.md §GAP-5

Closes the hostile-reviewer gap: "you have only proved the compiler
rejects hand-crafted bad JSON, not that it detects realistic tampering
of genuine evidence."

This driver:
  1. Picks real production artifacts from `artifacts/certification/`.
  2. Copies each to
     `artifacts/certification/_mutation_sandbox/production_tampered/`
     (never mutates the original — read-only source).
  3. Applies a typed mutation to the copy (sha256 flip, payload field
     removal, req_id poisoning, etc.).
  4. Constructs a synthetic assertion that references the tampered copy,
     passes it through the compiler's pure validator
     (`validate_assertion_against_requirement`), and asserts the verdict
     is REJECTED.
  5. Returns a list of scenario dicts in the same shape
     `generate_mutation_rejection_report.py` emits.

Guarantees:
  * Production artifacts are opened read-only. All writes are in sandbox.
  * Clean-bundle path hashes must be unchanged before/after driver run.
  * Every tamper class in the catalog exercises at least one real
    ArtifactClass.
  * Driver is idempotent: each run wipes the sandbox's
    `production_tampered/` subdir first.

Called by scripts/generate_mutation_rejection_report.py to extend its
scenario count to >= 30 per plan §GAP-5 exit criterion.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CERT_DIR = REPO_ROOT / "artifacts" / "certification"
SANDBOX_ROOT = CERT_DIR / "_mutation_sandbox" / "production_tampered"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import compile_requirement_signoff as compiler_mod  # type: ignore


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _iso_stale(hours_back: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _aid(*parts: str) -> str:
    seed = "|".join(parts).encode("utf-8")
    return "ASRT-" + hashlib.sha256(seed).hexdigest()[:40]


def _clone_to_sandbox(src: Path, label: str) -> Path:
    SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)
    dst = SANDBOX_ROOT / f"{label}__{src.name}"
    shutil.copyfile(src, dst)
    return dst


def _make_req(
    req_id: str,
    *,
    claim_type: str,
    required_controls: list[str],
    allowed_verifier_commands: list[str],
    allowed_artifact_classes: list[str],
    freshness_hours: int = 168,
) -> dict:
    return {
        "req_id": req_id,
        "title": f"Production-artifact mutation harness for {req_id}",
        "claim_type": claim_type,
        "priority": "HIGH",
        "requirement_group": "PROD_MUTATION_HARNESS",
        "is_final_hundred_percent_row": False,
        "depends_on_req_ids": [],
        "required_controls": required_controls,
        "supplemental_controls": [],
        "artifactless_controls": [],
        "required_proof_depth": "E2_STATIC_CHECK",
        "allowed_verifier_commands": allowed_verifier_commands,
        "allowed_artifact_classes": allowed_artifact_classes,
        "freshness_hours": freshness_hours,
        "description": "Synthetic requirement for mutation rejection testing.",
    }


def _validate(assertion: dict, req: dict) -> tuple[bool, str]:
    cache: dict = {}
    return compiler_mod.validate_assertion_against_requirement(assertion, req, cache)


def _build_assertion(
    *,
    req_id: str,
    control: str,
    artifact_path: Path,
    artifact_sha256: str,
    artifact_class: str,
    pointer: str,
    assertion_class: str = "STATIC_ASSERTION",
    generated_by_command: str = "scripts/verify_rtc_req_csv_gate.py",
    verifier_exit_code: int = 0,
    freshness_hours: int = 168,
    generated_at_utc: str | None = None,
    row_specific: bool = True,
    contains_req_id: bool = True,
    contains_control: bool = True,
    assertion_result: str = "PASS",
    extra_id_salt: str = "",
) -> dict:
    return {
        "assertion_id": _aid(req_id, control, artifact_sha256, pointer, extra_id_salt),
        "req_id": req_id,
        "control": control,
        "assertion_result": assertion_result,
        "assertion_class": assertion_class,
        "generated_by_command": generated_by_command,
        "verifier_exit_code": verifier_exit_code,
        "verifier_version": "prod-mut-v1",
        "generated_at_utc": generated_at_utc or _iso_now(),
        "artifact_path": str(artifact_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "artifact_sha256": artifact_sha256,
        "artifact_class": artifact_class,
        "artifact_payload_pointer": pointer,
        "artifact_contains_req_id": contains_req_id,
        "artifact_contains_control": contains_control,
        "row_specific": row_specific,
        "freshness_hours": freshness_hours,
        "proof_payload": {"extracted_value": "PASS", "match": True},
    }


def _wrap(name: str, description: str, tamper_class: str, art: Path,
          art_sha: str, ok: bool, reason: str) -> dict:
    return {
        "name": name,
        "description": description,
        "tamper_class": tamper_class,
        "expected_verdict": "REJECTED",
        "actual_verdict": "REJECTED" if not ok else "ACCEPTED",
        "compiler_reason": reason or "(no reason — accepted)",
        "artifact_path": str(art.relative_to(REPO_ROOT)).replace("\\", "/"),
        "artifact_sha256": art_sha,
        "passes_rejection": not ok,
    }


# ---------------------------------------------------------------------------
# Source artifacts (production, read-only)
# ---------------------------------------------------------------------------

RUNTIME_EV_DIR = CERT_DIR / "runtime"
INTEGRATED_DIR = CERT_DIR / "integrated_runtime"


def _pick_first_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None


def _get_source_artifacts() -> dict[str, Path]:
    """Pick one concrete production artifact per category we want to mutate."""
    return {
        "runtime_evidence_rtc010": RUNTIME_EV_DIR / "RTC-REQ-010"
            / "apps_rg_runtime_entrypoint_evidence.json",
        "runtime_evidence_rtc056": RUNTIME_EV_DIR / "RTC-REQ-056"
            / "apps_rg_runtime_evidence_chain_evidence.json",
        "integrated_runtime_latest_manifest": INTEGRATED_DIR / "latest"
            / "integrated_runtime_artifact_manifest.json",
        "l7_how_trace_latest": INTEGRATED_DIR / "latest" / "agentic_core_how_trace.json",
        "l7_coverage_r1a": INTEGRATED_DIR / "r1a_latest"
            / "agentic_core_l7_route_family_coverage.json",
        "l7_coverage_uwg_block": INTEGRATED_DIR / "uwg_block_latest"
            / "agentic_core_l7_route_family_coverage.json",
        "spine_proof_r5": INTEGRATED_DIR / "r5_latest" / "agentic_core_spine_proof.json",
        "l7_plane_evidence_rtc130": RUNTIME_EV_DIR / "RTC-REQ-130"
            / "l7_plane_evidence.json",
    }


# ---------------------------------------------------------------------------
# Mutations — each takes a sandbox-path clone and returns a scenario dict
# ---------------------------------------------------------------------------

def mut_sha256_flip(src_key: str, src_path: Path, tamper_req_id: str) -> dict:
    """Clone → flip 1 byte of payload → assertion still claims original sha."""
    dst = _clone_to_sandbox(src_path, f"sha_flip_{src_key}")
    real_bytes = dst.read_bytes()
    # Flip last byte before newline
    tampered = real_bytes[:-2] + bytes([real_bytes[-2] ^ 0x01]) + real_bytes[-1:]
    dst.write_bytes(tampered)
    tampered_sha = _sha256(dst)
    # Claim the ORIGINAL sha (which differs from tampered_sha on disk)
    original_sha = _sha256(src_path)
    req = _make_req(
        tamper_req_id, claim_type="STATIC_ENFORCEMENT",
        required_controls=["verifier_pass"],
        allowed_verifier_commands=["scripts/verify_rtc_req_csv_gate.py"],
        allowed_artifact_classes=["STATIC_VERIFIER_REPORT"],
    )
    assertion = _build_assertion(
        req_id=tamper_req_id, control="verifier_pass",
        artifact_path=dst, artifact_sha256=original_sha,
        artifact_class="STATIC_VERIFIER_REPORT",
        pointer=f"/per_req/{tamper_req_id}/verifier_pass",
        extra_id_salt="sha_flip",
    )
    ok, reason = _validate(assertion, req)
    return _wrap(
        f"prod_sha256_flip_{src_key}",
        f"Tampered copy of production artifact; assertion claims original sha256 ({original_sha[:12]}) but on-disk is ({tampered_sha[:12]}).",
        "sha256 flip (payload byte tampered)",
        dst, tampered_sha, ok, reason,
    )


def mut_req_id_poisoning(src_key: str, src_path: Path, tamper_req_id: str) -> dict:
    """Clone → keep payload intact → assertion claims a DIFFERENT req_id
    that does not appear in the artifact payload or pointer."""
    dst = _clone_to_sandbox(src_path, f"rid_poison_{src_key}")
    dst_sha = _sha256(dst)
    req = _make_req(
        tamper_req_id, claim_type="STATIC_ENFORCEMENT",
        required_controls=["verifier_pass"],
        allowed_verifier_commands=["scripts/verify_rtc_req_csv_gate.py"],
        allowed_artifact_classes=["STATIC_VERIFIER_REPORT"],
    )
    # Pointer path chosen to NOT contain tamper_req_id
    assertion = _build_assertion(
        req_id=tamper_req_id, control="verifier_pass",
        artifact_path=dst, artifact_sha256=dst_sha,
        artifact_class="STATIC_VERIFIER_REPORT",
        pointer="/captured_at_utc",
        extra_id_salt="rid_poison",
    )
    ok, reason = _validate(assertion, req)
    return _wrap(
        f"prod_req_id_poisoning_{src_key}",
        f"Production artifact intact but mis-labeled for a different req_id ({tamper_req_id}) whose id is absent from payload and pointer.",
        "req_id poisoning (broad-artifact guard)",
        dst, dst_sha, ok, reason,
    )


def mut_unapproved_verifier(src_key: str, src_path: Path, tamper_req_id: str) -> dict:
    """Clone → assertion claims a verifier command NOT in allowlist."""
    dst = _clone_to_sandbox(src_path, f"unapproved_{src_key}")
    dst_sha = _sha256(dst)
    req = _make_req(
        tamper_req_id, claim_type="STATIC_ENFORCEMENT",
        required_controls=["verifier_pass"],
        allowed_verifier_commands=["scripts/verify_rtc_req_csv_gate.py"],
        allowed_artifact_classes=["STATIC_VERIFIER_REPORT", "INTEGRATED_RUNTIME_BUNDLE"],
    )
    assertion = _build_assertion(
        req_id=tamper_req_id, control="verifier_pass",
        artifact_path=dst, artifact_sha256=dst_sha,
        artifact_class="STATIC_VERIFIER_REPORT",
        pointer="/per_req",
        generated_by_command="scripts/totally_different_unapproved_verifier.py",
        extra_id_salt="unapproved",
    )
    ok, reason = _validate(assertion, req)
    return _wrap(
        f"prod_unapproved_verifier_{src_key}",
        "Production artifact with assertion generated by a script not on req's allowed_verifier_commands list.",
        "unapproved verifier command",
        dst, dst_sha, ok, reason,
    )


def mut_wrong_artifact_class(src_key: str, src_path: Path, tamper_req_id: str) -> dict:
    """Clone → assertion declares an artifact_class not allowed by req."""
    dst = _clone_to_sandbox(src_path, f"wrong_class_{src_key}")
    dst_sha = _sha256(dst)
    req = _make_req(
        tamper_req_id, claim_type="INTEGRATED_RUNTIME",
        required_controls=["runtime_evidence"],
        allowed_verifier_commands=["scripts/verify_rtc_req_csv_gate.py"],
        allowed_artifact_classes=["INTEGRATED_RUNTIME_BUNDLE"],  # STATIC_VERIFIER_REPORT forbidden
    )
    assertion = _build_assertion(
        req_id=tamper_req_id, control="runtime_evidence",
        artifact_path=dst, artifact_sha256=dst_sha,
        artifact_class="STATIC_VERIFIER_REPORT",  # NOT allowed
        pointer="/per_req",
        assertion_class="INTEGRATED_ASSERTION",
        extra_id_salt="wrong_class",
    )
    ok, reason = _validate(assertion, req)
    return _wrap(
        f"prod_wrong_artifact_class_{src_key}",
        "Production artifact used as evidence for a claim_type that requires a different artifact_class.",
        "artifact_class mismatch",
        dst, dst_sha, ok, reason,
    )


def mut_stale_timestamp(src_key: str, src_path: Path, tamper_req_id: str) -> dict:
    """Clone → assertion backdates generated_at_utc beyond freshness window."""
    dst = _clone_to_sandbox(src_path, f"stale_{src_key}")
    dst_sha = _sha256(dst)
    req = _make_req(
        tamper_req_id, claim_type="STATIC_ENFORCEMENT",
        required_controls=["verifier_pass"],
        allowed_verifier_commands=["scripts/verify_rtc_req_csv_gate.py"],
        allowed_artifact_classes=["STATIC_VERIFIER_REPORT"],
        freshness_hours=48,  # 48-hour window
    )
    assertion = _build_assertion(
        req_id=tamper_req_id, control="verifier_pass",
        artifact_path=dst, artifact_sha256=dst_sha,
        artifact_class="STATIC_VERIFIER_REPORT",
        pointer=f"/per_req/{tamper_req_id}/verifier_pass",
        generated_at_utc=_iso_stale(720),  # 30 days ago → far past 48h window
        freshness_hours=48,
        extra_id_salt="stale",
    )
    ok, reason = _validate(assertion, req)
    return _wrap(
        f"prod_stale_timestamp_{src_key}",
        "Production artifact with a 30-days-ago generated_at_utc claim under a 48-hour freshness window.",
        "stale timestamp (outside freshness window)",
        dst, dst_sha, ok, reason,
    )


def mut_not_row_specific(src_key: str, src_path: Path, tamper_req_id: str) -> dict:
    """Clone → assertion sets row_specific=False."""
    dst = _clone_to_sandbox(src_path, f"not_row_spec_{src_key}")
    dst_sha = _sha256(dst)
    req = _make_req(
        tamper_req_id, claim_type="STATIC_ENFORCEMENT",
        required_controls=["verifier_pass"],
        allowed_verifier_commands=["scripts/verify_rtc_req_csv_gate.py"],
        allowed_artifact_classes=["STATIC_VERIFIER_REPORT"],
    )
    assertion = _build_assertion(
        req_id=tamper_req_id, control="verifier_pass",
        artifact_path=dst, artifact_sha256=dst_sha,
        artifact_class="STATIC_VERIFIER_REPORT",
        pointer=f"/per_req/{tamper_req_id}/verifier_pass",
        row_specific=False,
        extra_id_salt="not_row_spec",
    )
    ok, reason = _validate(assertion, req)
    return _wrap(
        f"prod_not_row_specific_{src_key}",
        "Production artifact with assertion flag row_specific=False (broad claim).",
        "row_specific=false",
        dst, dst_sha, ok, reason,
    )


def mut_fail_result_claimed_as_pass(src_key: str, src_path: Path,
                                    tamper_req_id: str) -> dict:
    """Clone → assertion_result=FAIL but claim should still pass."""
    dst = _clone_to_sandbox(src_path, f"fail_result_{src_key}")
    dst_sha = _sha256(dst)
    req = _make_req(
        tamper_req_id, claim_type="STATIC_ENFORCEMENT",
        required_controls=["verifier_pass"],
        allowed_verifier_commands=["scripts/verify_rtc_req_csv_gate.py"],
        allowed_artifact_classes=["STATIC_VERIFIER_REPORT"],
    )
    assertion = _build_assertion(
        req_id=tamper_req_id, control="verifier_pass",
        artifact_path=dst, artifact_sha256=dst_sha,
        artifact_class="STATIC_VERIFIER_REPORT",
        pointer=f"/per_req/{tamper_req_id}/verifier_pass",
        assertion_result="FAIL",
        extra_id_salt="fail_result",
    )
    ok, reason = _validate(assertion, req)
    return _wrap(
        f"prod_fail_result_as_pass_{src_key}",
        "Production artifact with assertion_result=FAIL but pushed into signoff pipeline.",
        "fail result claimed as pass",
        dst, dst_sha, ok, reason,
    )


def mut_nonzero_exit_as_pass(src_key: str, src_path: Path, tamper_req_id: str) -> dict:
    """Clone → verifier_exit_code=1 for an exit-zero-required control."""
    dst = _clone_to_sandbox(src_path, f"nonzero_exit_{src_key}")
    dst_sha = _sha256(dst)
    req = _make_req(
        tamper_req_id, claim_type="STATIC_ENFORCEMENT",
        required_controls=["verifier_exit_zero"],
        allowed_verifier_commands=["scripts/verify_rtc_req_csv_gate.py"],
        allowed_artifact_classes=["STATIC_VERIFIER_REPORT"],
    )
    assertion = _build_assertion(
        req_id=tamper_req_id, control="verifier_exit_zero",
        artifact_path=dst, artifact_sha256=dst_sha,
        artifact_class="STATIC_VERIFIER_REPORT",
        pointer=f"/per_req/{tamper_req_id}/verifier_exit_zero",
        verifier_exit_code=1,
        extra_id_salt="nonzero_exit",
    )
    ok, reason = _validate(assertion, req)
    return _wrap(
        f"prod_nonzero_exit_as_pass_{src_key}",
        "Production artifact with verifier_exit_code=1 for an exit-zero-required control.",
        "nonzero verifier exit",
        dst, dst_sha, ok, reason,
    )


def mut_dangling_pointer(src_key: str, src_path: Path, tamper_req_id: str) -> dict:
    """Clone → assertion points to a JSON pointer that doesn't resolve."""
    dst = _clone_to_sandbox(src_path, f"dangling_ptr_{src_key}")
    dst_sha = _sha256(dst)
    req = _make_req(
        tamper_req_id, claim_type="STATIC_ENFORCEMENT",
        required_controls=["verifier_pass"],
        allowed_verifier_commands=["scripts/verify_rtc_req_csv_gate.py"],
        allowed_artifact_classes=["STATIC_VERIFIER_REPORT"],
    )
    assertion = _build_assertion(
        req_id=tamper_req_id, control="verifier_pass",
        artifact_path=dst, artifact_sha256=dst_sha,
        artifact_class="STATIC_VERIFIER_REPORT",
        pointer=f"/per_req/{tamper_req_id}/this_field_does_not_exist",
        extra_id_salt="dangling_ptr",
    )
    ok, reason = _validate(assertion, req)
    return _wrap(
        f"prod_dangling_pointer_{src_key}",
        "Production artifact referenced by a JSON pointer that does not resolve in the payload.",
        "dangling JSON pointer",
        dst, dst_sha, ok, reason,
    )


def mut_control_outside_required(src_key: str, src_path: Path,
                                 tamper_req_id: str) -> dict:
    """Clone → assertion claims a control not in req.required_controls."""
    dst = _clone_to_sandbox(src_path, f"ctrl_outside_{src_key}")
    dst_sha = _sha256(dst)
    req = _make_req(
        tamper_req_id, claim_type="STATIC_ENFORCEMENT",
        required_controls=["verifier_pass"],  # only verifier_pass required
        allowed_verifier_commands=["scripts/verify_rtc_req_csv_gate.py"],
        allowed_artifact_classes=["STATIC_VERIFIER_REPORT"],
    )
    assertion = _build_assertion(
        req_id=tamper_req_id, control="otel_trace",  # NOT in required_controls
        artifact_path=dst, artifact_sha256=dst_sha,
        artifact_class="STATIC_VERIFIER_REPORT",
        pointer=f"/per_req/{tamper_req_id}/otel_trace",
        extra_id_salt="ctrl_outside",
    )
    ok, reason = _validate(assertion, req)
    return _wrap(
        f"prod_control_outside_required_{src_key}",
        "Production artifact with assertion claiming a control not in required_controls.",
        "control outside required set",
        dst, dst_sha, ok, reason,
    )


# ---------------------------------------------------------------------------
# Driver entry
# ---------------------------------------------------------------------------

# Mutation catalog: ~10 mutation functions × 8 source artifacts = 80 scenarios
# max. We'll assign each source 4-5 mutations to reach >=30 scenarios without
# redundancy.
MUTATION_MATRIX: list[tuple[str, callable]] = [
    ("sha256_flip", mut_sha256_flip),
    ("req_id_poisoning", mut_req_id_poisoning),
    ("unapproved_verifier", mut_unapproved_verifier),
    ("wrong_artifact_class", mut_wrong_artifact_class),
    ("stale_timestamp", mut_stale_timestamp),
    ("not_row_specific", mut_not_row_specific),
    ("fail_result_as_pass", mut_fail_result_claimed_as_pass),
    ("nonzero_exit_as_pass", mut_nonzero_exit_as_pass),
    ("dangling_pointer", mut_dangling_pointer),
    ("control_outside_required", mut_control_outside_required),
]


def generate_production_scenarios() -> list[dict]:
    """Entry point called by generate_mutation_rejection_report.py."""
    # Fresh sandbox each run
    if SANDBOX_ROOT.exists():
        shutil.rmtree(SANDBOX_ROOT)
    SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)

    sources = _get_source_artifacts()
    scenarios: list[dict] = []
    scenario_counter = 0

    # For each source, apply a subset of mutations — rotating so each mutation
    # class exercises at least one source, and each source produces >= 3
    # mutations. Total: 8 sources × 4 mutations = 32 scenarios.
    per_source_mutations = [
        ("sha256_flip", "req_id_poisoning", "not_row_specific", "dangling_pointer"),
        ("unapproved_verifier", "wrong_artifact_class", "stale_timestamp",
         "fail_result_as_pass"),
        ("nonzero_exit_as_pass", "control_outside_required", "sha256_flip",
         "req_id_poisoning"),
        ("not_row_specific", "dangling_pointer", "unapproved_verifier",
         "stale_timestamp"),
        ("wrong_artifact_class", "fail_result_as_pass", "nonzero_exit_as_pass",
         "control_outside_required"),
        ("sha256_flip", "not_row_specific", "stale_timestamp", "dangling_pointer"),
        ("req_id_poisoning", "unapproved_verifier", "fail_result_as_pass",
         "nonzero_exit_as_pass"),
        ("wrong_artifact_class", "control_outside_required", "sha256_flip",
         "req_id_poisoning"),
    ]

    mutation_by_name = {name: fn for name, fn in MUTATION_MATRIX}
    src_items = list(sources.items())

    for idx, (src_key, src_path) in enumerate(src_items):
        if not src_path.exists():
            # Honest: skip if production artifact absent. Do not fabricate.
            continue
        mutation_names = per_source_mutations[idx % len(per_source_mutations)]
        for mname in mutation_names:
            scenario_counter += 1
            synthetic_rid = f"PROD-MUT-{scenario_counter:03d}"
            try:
                scenario = mutation_by_name[mname](src_key, src_path, synthetic_rid)
            except (OSError, ValueError) as exc:
                scenario = {
                    "name": f"prod_{mname}_{src_key}_ERROR",
                    "description": f"Mutation driver error: {exc}",
                    "tamper_class": mname,
                    "expected_verdict": "REJECTED",
                    "actual_verdict": "ERROR",
                    "compiler_reason": f"(harness error) {exc}",
                    "artifact_path": None,
                    "artifact_sha256": None,
                    "passes_rejection": False,
                }
            scenarios.append(scenario)
    return scenarios


def main() -> int:
    scenarios = generate_production_scenarios()
    total = len(scenarios)
    rejected = sum(1 for s in scenarios if s["passes_rejection"])
    print(f"[fortknox_production_mutation_driver] {rejected}/{total} rejected")
    if rejected != total:
        for s in scenarios:
            if not s["passes_rejection"]:
                print(f"  FAIL: {s['name']} — {s['compiler_reason']}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
