"""W2 verifier #2 — R1B safe-reuse integrated-runtime decision is real.

Asserts the SafeReuseDecision artifact:
  1. dense_candidate_produced is True (D2 hit was real).
  2. veto_invoked is True.
  3. allow aligned with veto_outcome:
       allow=True  iff veto_outcome=ALLOWED
       allow=False iff veto_outcome in {BLOCKED, UNKNOWN, ERROR, TIMEOUT, PARSE_FAIL}
  4. The 4 explicit safety-metric aliases are present (W2 §Metric cleanup).
  5. unsafe_reuse_allowed_count == 0 (the entry point never admits unsafe).
  6. unknown_error_timeout_parse_fail_block_count is 1 ONLY when the
     veto outcome is in the fail-closed set.
  7. The RuntimeGateVerdictBundle confirms the same veto_outcome value
     (cross-artifact consistency).
  8. When veto_primary_mode == C_PRIMARY_LLM_JUDGE and veto_outcome == ALLOWED,
     llm_judge_invocation_count >= 1 (lexical-only path cannot pass).
"""

from __future__ import annotations

import sys

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from _w2_verifier_common import (
    EXIT_HARNESS_ERROR,
    fail,
    load_payload,
    passed,
    resolve_artifact_dir,
)

import json

REQUIRED_ALIASES = (
    "unsafe_reuse_allowed_count",
    "safe_reuse_blocked_count",
    "hard_negative_allowed_count",
    "unknown_error_timeout_parse_fail_block_count",
)
FAIL_CLOSED_OUTCOMES = {"UNKNOWN", "ERROR", "TIMEOUT", "PARSE_FAIL"}

# W2b § 6 — rejection matrix. These reason codes are consumed by CI +
# verifier_results.json.
W2B_APPROVED_PROVIDERS = frozenset({"local_qwen", "anthropic_haiku"})
W2B_REQUIRED_ATTESTATION_KEYS = frozenset({
    "schema_version", "attestation_kind", "provider", "model_id",
    "rubric_hash_sha256", "response_hash_sha256", "response_hash_mode",
    "verdict", "confidence", "veto_stage_class",
    "deterministic_proof_stage_used", "x3_disposition",
    "safe_reuse_allow", "mock_safe_used", "approved_provider",
})


def _verify_live_provider_attestation(art_dir) -> tuple[bool, str, str]:
    """W2b § 6 — 8-row rejection matrix for live_provider_attestation.json.

    Returns ``(ok, reason_code, detail)``. ``reason_code`` is empty on PASS.
    """
    att_path = art_dir / "live_provider_attestation.json"
    if not att_path.exists():
        return False, "REJECT_MISSING_ATTESTATION", str(att_path)
    try:
        att = json.loads(att_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, "REJECT_ATTESTATION_SCHEMA_INVALID", f"{exc}"
    if not isinstance(att, dict):
        return False, "REJECT_ATTESTATION_SCHEMA_INVALID", "not a JSON object"
    missing = W2B_REQUIRED_ATTESTATION_KEYS - set(att.keys())
    if missing:
        return False, "REJECT_ATTESTATION_SCHEMA_INVALID", f"missing_keys={sorted(missing)}"
    provider = att.get("provider")
    if provider == "mock_safe" or att.get("mock_safe_used"):
        return False, "REJECT_MOCK_SAFE_IN_CERTIFICATION", f"provider={provider}"
    if provider not in W2B_APPROVED_PROVIDERS:
        return False, "REJECT_UNAPPROVED_PROVIDER", f"provider={provider}"
    if att.get("deterministic_proof_stage_used"):
        return (False, "REJECT_DETERMINISTIC_PROOF_STAGE_IN_CERTIFICATION",
                "deterministic_proof_stage_used=True")
    if att.get("veto_stage_class") != "LLMJudgeVeto":
        return (False, "REJECT_UNAPPROVED_VETO_STAGE_CLASS",
                f"veto_stage_class={att.get('veto_stage_class')!r}")
    verdict = att.get("verdict")
    if verdict != "SAFE":
        return False, "REJECT_NON_SAFE_AS_ALLOW", f"verdict={verdict!r}"
    if att.get("safe_reuse_allow") is not True:
        return False, "REJECT_NON_SAFE_AS_ALLOW", "safe_reuse_allow != True"
    if att.get("x3_disposition") != "X3D":
        return (False, "REJECT_NON_SAFE_AS_ALLOW",
                f"x3_disposition={att.get('x3_disposition')!r}")
    if verdict == "SAFE" and not att.get("rubric_hash_sha256"):
        return False, "REJECT_SAFE_WITHOUT_RUBRIC_HASH", "empty rubric_hash_sha256"
    if verdict == "SAFE" and not att.get("response_hash_sha256"):
        return False, "REJECT_SAFE_WITHOUT_RESPONSE_HASH", "empty response_hash_sha256"
    return True, "", (
        f"provider={provider}, verdict=SAFE, "
        f"confidence={att.get('confidence')}"
    )


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    print(f"[verify_r1b_safe_reuse_integrated_runtime] artifact_dir={art_dir}")

    try:
        sr = load_payload(art_dir, "semantic_cache_safe_reuse_decision.json")
        gate = load_payload(art_dir, "runtime_gate_verdict_bundle.json")
        manifest = load_payload(art_dir, "integrated_runtime_artifact_manifest.json")
    except FileNotFoundError as exc:
        return fail("ARTIFACT_MISSING", str(exc))

    # W2 proof-hardening — the canonical acceptance run MUST use the
    # approved C-primary LLMJudgeVeto, with NO DeterministicProofStage in
    # the stack. STRUCTURAL_ONLY runs are legitimate but cannot certify.
    match_status = manifest.get("veto_stage_match_status", "")
    det_used = bool(manifest.get("deterministic_proof_stage_used", False))
    veto_actual = manifest.get("veto_stage_actual", "")
    veto_expected = manifest.get("veto_stage_expected", "LLMJudgeVeto")
    if match_status != "PASS":
        return fail("VETO_STAGE_MATCH_STATUS_NOT_PASS",
                    f"match_status={match_status!r}; actual={veto_actual!r}; "
                    f"expected={veto_expected!r}; deterministic_proof_stage_used={det_used}")
    if det_used:
        return fail("DETERMINISTIC_PROOF_STAGE_IN_ACCEPTANCE_RUN",
                    f"proof_only_stages={manifest.get('proof_only_stage_names')}")
    if veto_actual != veto_expected:
        return fail("VETO_STAGE_CLASS_MISMATCH",
                    f"actual={veto_actual!r} != expected={veto_expected!r}")
    # Veto counters must sum to exactly 1 (exactly one outcome per run).
    counters = manifest.get("veto_counters", {}) or {}
    total = sum(int(v) for k, v in counters.items()
                if k in {"allowed_count", "blocked_count", "unknown_count",
                         "error_count", "timeout_count", "parse_fail_count",
                         "not_invoked_count"})
    if total != 1:
        return fail("VETO_COUNTERS_INCONSISTENT",
                    f"sum of exclusive counters={total} (expected 1): {counters}")

    # 1+2: dense + veto.
    if not sr.get("dense_candidate_produced"):
        return fail("DENSE_CANDIDATE_NOT_PRODUCED",
                    "safe_reuse.dense_candidate_produced must be True for an integrated-runtime PASS")
    if not sr.get("veto_invoked"):
        return fail("VETO_NOT_INVOKED",
                    "safe_reuse.veto_invoked must be True when dense candidate produced")

    # 3: allow ↔ veto_outcome alignment.
    allow = bool(sr.get("allow"))
    sr_outcome = sr.get("veto_outcome", "")
    if allow and sr_outcome != "ALLOWED":
        return fail("ALLOW_WITHOUT_ALLOWED_VETO",
                    f"allow=True but veto_outcome={sr_outcome!r}")
    if (not allow) and sr_outcome == "ALLOWED" and sr.get("dense_candidate_produced"):
        return fail("ALLOWED_VETO_WITHOUT_ALLOW",
                    "veto allowed but safe_reuse.allow=False")

    # 4: explicit safety-metric aliases present.
    missing_aliases = [a for a in REQUIRED_ALIASES if a not in sr]
    if missing_aliases:
        return fail("METRIC_ALIASES_MISSING",
                    f"missing safety-metric aliases: {missing_aliases}")

    # 5: never admit unsafe.
    if int(sr.get("unsafe_reuse_allowed_count", 0)) > 0:
        return fail("UNSAFE_REUSE_ADMITTED",
                    f"unsafe_reuse_allowed_count={sr.get('unsafe_reuse_allowed_count')}")

    # 6: fail-closed counter consistency.
    fcb = int(sr.get("unknown_error_timeout_parse_fail_block_count", 0))
    if sr_outcome in FAIL_CLOSED_OUTCOMES:
        if fcb != 1:
            return fail("FAIL_CLOSED_COUNTER_MISMATCH",
                        f"veto_outcome={sr_outcome} but unknown_error_timeout_parse_fail_block_count={fcb}")
    else:
        if fcb != 0:
            return fail("FAIL_CLOSED_COUNTER_FALSE_POSITIVE",
                        f"veto_outcome={sr_outcome} but unknown_error_timeout_parse_fail_block_count={fcb}")

    # 7: cross-artifact consistency.
    gate_outcome = gate.get("veto_outcome", "")
    if gate_outcome != sr_outcome:
        return fail("GATE_DECISION_OUTCOME_DIVERGENCE",
                    f"gate.veto_outcome={gate_outcome!r} != safe_reuse.veto_outcome={sr_outcome!r}")

    # 8: lexical-only path cannot PASS.
    primary_mode = gate.get("veto_primary_mode", "")
    llm_count = int(gate.get("llm_judge_invocation_count", 0))
    if allow and primary_mode == "C_PRIMARY_LLM_JUDGE" and llm_count < 1:
        return fail("LEXICAL_ONLY_BYPASS",
                    f"allow=True with C_PRIMARY_LLM_JUDGE but llm_judge_invocation_count={llm_count}")

    # W2b § 6 — live-provider attestation gate for the ALLOW path.
    # Only enforced when the canonical run is actually an allow run
    # (allow=True). Fail-closed runs do not require an attestation.
    if allow:
        ok, reason, detail = _verify_live_provider_attestation(art_dir)
        if not ok:
            return fail(reason, detail)

    return passed(
        f"safe_reuse.allow={allow}, veto_outcome={sr_outcome}, "
        f"llm_judge_invocations={llm_count}, "
        f"unsafe_reuse_allowed_count=0, hard_negatives={sr.get('hard_negative_allowed_count')}"
    )


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
