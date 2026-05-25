"""Generate the final 100% runtime proof bundle.

Walks the Fort Knox certification surface end-to-end and emits a single
deterministic JSON artifact at:

    artifacts/certification/HUNDRED_PERCENT_RUNTIME_PROOF.json

The bundle is the minimum-trusted-input view: every claim resolves to a
file-on-disk sha256, every verifier exit code is captured, and every
substrate is enumerated. A reviewer who trusts only this script and the
referenced files can independently confirm the 100% claim.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHAINS_DIR = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime"
OUT_PATH = REPO_ROOT / "artifacts" / "certification" / "HUNDRED_PERCENT_RUNTIME_PROOF.json"

CHAINS = [
    ("latest",            "R1B_SEMANTIC_CACHE",              "verify_r1b_safe_reuse_integrated_runtime"),
    ("mw_latest",         "MANAGED_WORKFLOW_STRUCTURAL",     None),
    ("r1a_latest",        "R1A_EXACT_CACHE",                 "verify_r1a_exact_cache_l7_runtime"),
    ("r5_latest",         "R5_FALLBACK",                     "verify_r5_fallback_l7_runtime"),
    ("uwg_block_latest",  "UWG_BLOCK_PATH",                  "verify_uwg_block_path_l7_runtime"),
    ("uwg_commit_latest", "UWG_COMMIT_PATH",                 "verify_uwg_commit_path_l7_runtime"),
    ("r3_latest",         "R3_GROUNDED_READ",                "verify_r3_grounded_read_l7_runtime"),
    ("r4_latest",         "R4_SINGLE_ACTION",                "verify_r4_single_action_l7_runtime"),
    ("mw_real_latest",    "MANAGED_WORKFLOW_REAL_EXECUTION", "verify_mw_real_execution_l7_runtime"),
]
COMMON_VERIFIERS = [
    "verify_integrated_runtime_artifact_chain",
    "verify_integrated_runtime_entrypoint",
    "verify_spine_proof_bundle",
    "verify_integrated_runtime_manifest_exact_refs",
    "verify_agentic_core_how_trace",
    "verify_l7_fortknox_evidence",
    "verify_agentic_core_l7_route_family_coverage",
]


def _sha256(p: Path) -> str:
    if not p.exists():
        return ""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _read_payload(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return d.get("payload", {}) if isinstance(d, dict) else {}


def _run_verifier(name: str, art_dir: Path) -> dict:
    env = os.environ.copy()
    env["W2_ARTIFACT_DIR"] = str(art_dir)
    t0 = time.perf_counter()
    r = subprocess.run(
        [sys.executable, "-m", f"ops_scripts.ci.{name}"],
        env=env, capture_output=True, text=True, timeout=60,
    )
    return {
        "verifier": name,
        "exit_code": r.returncode,
        "passed": r.returncode == 0,
        "duration_ms": int((time.perf_counter() - t0) * 1000),
        "tail": (r.stdout or "").strip().splitlines()[-1:],
    }


def _chain_summary(chain: str, family: str, family_verifier: str | None) -> dict:
    art = CHAINS_DIR / chain
    if not art.exists():
        return {"chain": chain, "family": family, "exists": False}

    cov = _read_payload(art / "agentic_core_l7_route_family_coverage.json")
    fam_row = next(
        (
            f for f in (cov.get("route_families") or [])
            if isinstance(f, dict) and f.get("route_family") == family
        ),
        {},
    )
    spine = _read_payload(art / "agentic_core_spine_proof.json")
    manifest = _read_payload(art / "integrated_runtime_artifact_manifest.json")

    fk_dir = art / "fortknox_l7_evidence"
    fk_files = sorted(fk_dir.glob("*.json")) if fk_dir.is_dir() else []

    verifier_results: list[dict] = []
    for v in COMMON_VERIFIERS:
        verifier_results.append(_run_verifier(v, art))
    if family_verifier:
        verifier_results.append(_run_verifier(family_verifier, art))

    all_pass = all(v["passed"] for v in verifier_results)

    return {
        "chain": chain,
        "family": family,
        "exists": True,
        "chain_kind": manifest.get("chain_kind"),
        "spine_status": spine.get("agentic_core_spine_status"),
        "managed_workflow_certified": spine.get("managed_workflow_certified"),
        "synthetic_trace_detected": spine.get("synthetic_trace_detected"),
        "runtime_mode": spine.get("runtime_mode"),
        "coverage_certification_status": fam_row.get("certification_status"),
        "coverage_proof_class": fam_row.get("proof_class"),
        "fortknox_l7_evidence_count": len(fk_files),
        "manifest_sha256": _sha256(art / "integrated_runtime_artifact_manifest.json"),
        "spine_sha256": _sha256(art / "agentic_core_spine_proof.json"),
        "how_trace_sha256": _sha256(art / "agentic_core_how_trace.json"),
        "coverage_sha256": _sha256(art / "agentic_core_l7_route_family_coverage.json"),
        "verifier_results": verifier_results,
        "verifier_pass_count": sum(1 for v in verifier_results if v["passed"]),
        "verifier_total": len(verifier_results),
        "all_verifiers_pass": all_pass,
    }


def _live_attestation_summary() -> dict:
    """Summarize the R1B chain's live LLM provider attestation."""
    p = CHAINS_DIR / "latest" / "live_provider_attestation.json"
    if not p.exists():
        return {"present": False}
    a = json.loads(p.read_text(encoding="utf-8"))
    return {
        "present": True,
        "schema_version": a.get("schema_version"),
        "attestation_kind": a.get("attestation_kind"),
        "provider": a.get("provider"),
        "model_id": a.get("model_id"),
        "verdict": a.get("verdict"),
        "confidence": a.get("confidence"),
        "latency_ms": a.get("latency_ms"),
        "veto_stage_class": a.get("veto_stage_class"),
        "deterministic_proof_stage_used": a.get("deterministic_proof_stage_used"),
        "approved_provider": a.get("approved_provider"),
        "mock_safe_used": a.get("mock_safe_used"),
        "rubric_hash_sha256": a.get("rubric_hash_sha256"),
        "response_hash_sha256": a.get("response_hash_sha256"),
        "wall_clock_utc": a.get("wall_clock_utc"),
        "file_sha256": _sha256(p),
    }


def _signoff_summary() -> dict:
    """Read the compiled requirement-signoff report."""
    report_path = (
        REPO_ROOT / "artifacts" / "certification" / "final_requirement_signoff_report.json"
    )
    if not report_path.exists():
        return {"present": False}
    rep = json.loads(report_path.read_text(encoding="utf-8"))
    summary = rep.get("summary", {}) or {}
    sig_path = (
        REPO_ROOT / "artifacts" / "certification"
        / "final_requirement_signoff_report.signature.json"
    )
    merkle_path = (
        REPO_ROOT / "artifacts" / "certification"
        / "final_requirement_signoff_report.merkle.json"
    )
    sig = json.loads(sig_path.read_text(encoding="utf-8")) if sig_path.exists() else {}
    merkle = (
        json.loads(merkle_path.read_text(encoding="utf-8")) if merkle_path.exists() else {}
    )
    return {
        "present": True,
        "trust_level": rep.get("trust_level"),
        "requirement_count": summary.get("total"),
        "signed_off_count": summary.get("signed_off"),
        "blocked_count": summary.get("blocked"),
        "not_verified_count": summary.get("not_verified"),
        "percent_signed_off": summary.get("percent_signed_off"),
        "by_claim_type": summary.get("by_claim_type"),
        "merkle_root": merkle.get("merkle_root") or rep.get("evidence_digest"),
        "evidence_digest": rep.get("evidence_digest"),
        "row_digest": rep.get("row_digest"),
        "git_commit": rep.get("git_commit"),
        "git_dirty": rep.get("git_dirty"),
        "compiler_sha256": rep.get("compiler_sha256"),
        "report_sha256": _sha256(report_path),
        "signature_status": sig.get("signature_verification_status"),
        "signer_id": sig.get("signer_id"),
        "signature_sha256": _sha256(sig_path),
        "merkle_sha256": _sha256(merkle_path),
    }


def _bundle_verification_summary() -> dict:
    """Run the bundle verifier and capture its summary."""
    t0 = time.perf_counter()
    r = subprocess.run(
        [sys.executable, "scripts/verify_final_requirement_signoff_bundle.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO_ROOT,
    )
    tail = (r.stdout or "").strip().splitlines()[-1:]
    return {
        "exit_code": r.returncode,
        "passed": r.returncode == 0,
        "duration_ms": int((time.perf_counter() - t0) * 1000),
        "tail": tail,
    }


def _mutation_summary() -> dict:
    p = REPO_ROOT / "artifacts" / "certification" / "fortknox_mutation_rejection_report.json"
    if not p.exists():
        return {"present": False}
    d = json.loads(p.read_text(encoding="utf-8"))
    return {
        "present": True,
        "scenarios_total": d.get("scenarios_total"),
        "scenarios_rejected": d.get("scenarios_rejected"),
        "clean_bundle_unchanged": d.get("clean_bundle_unchanged"),
        "overall_verdict": d.get("overall_verdict"),
        "file_sha256": _sha256(p),
    }


def main() -> int:
    print("[generate_100pct_runtime_proof] running per-chain verifier matrix...")
    chain_summaries = [_chain_summary(c, f, fv) for c, f, fv in CHAINS]
    total_verifiers = sum(c.get("verifier_total", 0) for c in chain_summaries)
    total_pass = sum(c.get("verifier_pass_count", 0) for c in chain_summaries)
    all_chains_pass = all(c.get("all_verifiers_pass", False) for c in chain_summaries)

    fams_certified = [
        c for c in chain_summaries
        if c.get("coverage_certification_status") == "CERTIFIED"
        and c.get("coverage_proof_class") == "REAL_RUNTIME"
    ]
    fams_structural = [
        c for c in chain_summaries
        if c.get("coverage_certification_status") == "STRUCTURAL_ONLY"
    ]

    real_runtime_pct = 100.0 * len(fams_certified) / max(1, len(chain_summaries))
    runnable_real_runtime_pct = 100.0 * len(fams_certified) / max(
        1, (len(chain_summaries) - len(fams_structural))
    )

    bundle = {
        "schema_version": 1,
        "generator": "tools/certification/generate_100pct_runtime_proof.py",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repo_root": str(REPO_ROOT),
        "headline_claims": {
            "runnable_route_families_real_runtime_pct": runnable_real_runtime_pct,
            "all_route_families_real_runtime_pct": real_runtime_pct,
            "all_chains_pass_all_verifiers": all_chains_pass,
            "verifier_pass_count": total_pass,
            "verifier_total": total_verifiers,
            "verifier_pass_pct": 100.0 * total_pass / max(1, total_verifiers),
            "fortknox_signed_off_count": None,  # filled below
            "fortknox_blocked_count": None,
            "fortknox_trust_level": None,
            "live_llm_provider_used_for_r1b_certification": None,
        },
        "route_family_certification_matrix": [
            {
                "family": c["family"],
                "chain_dir": c["chain"],
                "chain_kind": c.get("chain_kind"),
                "certification_status": c.get("coverage_certification_status"),
                "proof_class": c.get("coverage_proof_class"),
                "spine_status": c.get("spine_status"),
                "managed_workflow_certified": c.get("managed_workflow_certified"),
                "all_verifiers_pass": c.get("all_verifiers_pass"),
                "verifier_pass_count": c.get("verifier_pass_count"),
                "verifier_total": c.get("verifier_total"),
                "manifest_sha256": c.get("manifest_sha256"),
                "spine_sha256": c.get("spine_sha256"),
            }
            for c in chain_summaries
        ],
        "live_provider_attestation": _live_attestation_summary(),
        "fort_knox_signoff": _signoff_summary(),
        "bundle_verification": _bundle_verification_summary(),
        "mutation_rejection": _mutation_summary(),
        "per_chain_full_detail": chain_summaries,
        "remaining_external_gaps": {
            "GAP-2_external_attestation": {
                "status": "OPEN",
                "description": (
                    "Promotion to FINAL_SIGNED_CERTIFICATION requires an "
                    "external trust authority (cosign keyless via Sigstore "
                    "Fulcio under GitHub OIDC, or a KMS-backed long-lived "
                    "key). Repo-committed Ed25519 signer caps honestly at "
                    "SIGNED_PROOF."
                ),
                "remediation": (
                    "Wire cosign keyless in CI under GitHub OIDC; commit "
                    "Fulcio cert + rekor entry as "
                    "config/release_signer/cosign_bundle.json; extend "
                    "tools/cert/sign_with_ephemeral_key.py to detect bundle "
                    "and emit FINAL_SIGNED_CERTIFICATION."
                ),
                "blocks_100pct_runtime": False,
            },
        },
    }

    # Backfill headline claims that depend on signoff/bundle/attestation.
    so = bundle["fort_knox_signoff"]
    bundle["headline_claims"]["fortknox_signed_off_count"] = so.get("signed_off_count")
    bundle["headline_claims"]["fortknox_blocked_count"] = so.get("blocked_count")
    bundle["headline_claims"]["fortknox_trust_level"] = so.get("trust_level")
    att = bundle["live_provider_attestation"]
    bundle["headline_claims"]["live_llm_provider_used_for_r1b_certification"] = (
        att.get("provider") if att.get("present") else None
    )

    OUT_PATH.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Summary print
    h = bundle["headline_claims"]
    print(f"\n=== HEADLINE ===")
    print(f"  Runnable families REAL_RUNTIME:  {h['runnable_route_families_real_runtime_pct']:.1f}%  ({len(fams_certified)}/{len(chain_summaries)-len(fams_structural)})")
    print(f"  All families REAL_RUNTIME:        {h['all_route_families_real_runtime_pct']:.1f}%  ({len(fams_certified)}/{len(chain_summaries)})")
    print(f"  Verifier pass rate:               {h['verifier_pass_pct']:.1f}%  ({h['verifier_pass_count']}/{h['verifier_total']})")
    print(f"  Fort Knox signed_off:             {h['fortknox_signed_off_count']}/"
          f"{(so.get('signed_off_count') or 0) + (so.get('blocked_count') or 0) + (so.get('not_verified_count') or 0)}")
    print(f"  Fort Knox trust_level:            {h['fortknox_trust_level']}")
    print(f"  Live LLM provider (R1B):          {h['live_llm_provider_used_for_r1b_certification']}")
    print(f"  Bundle verification:              {'PASS' if bundle['bundle_verification']['passed'] else 'FAIL'}")
    print(f"  Mutation rejection:               {bundle['mutation_rejection'].get('overall_verdict')}")
    print(f"\nbundle written: {OUT_PATH.relative_to(REPO_ROOT)}")
    print(f"bundle sha256:  {_sha256(OUT_PATH)}")
    return 0 if all_chains_pass and so.get("blocked_count") == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
