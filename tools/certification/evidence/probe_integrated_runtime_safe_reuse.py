"""W2 — Integrated-runtime safe-reuse probe (triple-run).

Produces three evidence runs per invocation:

1. ``c_primary_allow/`` — real ``LLMJudgeVeto`` with a SAFE-producing
   provider (``anthropic_haiku`` if ``ANTHROPIC_API_KEY`` is set;
   ``local_qwen`` if vLLM is reachable; otherwise the approved-mock
   ``mock_safe`` gated on ``LLMJUDGEVETO_APPROVED_MOCK_SAFE=1``). If no
   SAFE-producing provider is available, this run is written with
   ``allow_path_attempted=True, allow_path_achieved=False`` and the
   composer emits ``R1B_INTEGRATED_RUNTIME_ALLOW_PATH_PROOF =
   INFRASTRUCTURE_GAP``. CANONICAL acceptance run — ``latest/`` mirrors
   this directory.

2. ``c_primary_fail_closed/`` — real ``LLMJudgeVeto`` with the
   policy-configured provider (local_qwen / anthropic_haiku / mock).
   Proves UNKNOWN/ERROR/TIMEOUT/PARSE_FAIL → fail-closed BLOCK. Uses the
   default ``mock`` provider (returns UNCERTAIN) if no live endpoint is
   reachable; that also drives fail-closed and is an honest proof.

3. ``structural_allow_topology/`` — ``DeterministicProofStage`` returns
   SAFE → drives the X3D ALLOW topology so all 12 artifacts populate.
   Proves chain structure only; labeled ``STRUCTURAL_ONLY`` in its
   manifest; composer refuses it for RTC-REQ-056 acceptance.

Composer acceptance rule:

    ``R1B_INTEGRATED_RUNTIME_PROOF = PASS`` requires BOTH
    ``R1B_INTEGRATED_RUNTIME_ALLOW_PATH_PROOF = PASS`` and
    ``R1B_INTEGRATED_RUNTIME_FAIL_CLOSED_PATH_PROOF = PASS``. Missing
    either keeps RTC-REQ-056 PARTIAL.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.entrypoints.integrated_safe_reuse_run import (
    PRODUCER_COMPONENT,
    run_integrated_safe_reuse,
)
from tools.certification.evidence._live_provider_attestation import (
    APPROVED_PROVIDERS,
    build_attestation_payload,
    write_attestation,
)
from tools.certification.safety.deterministic_proof_stage import DeterministicProofStage
from tools.certification.safety.llm_judge_veto import (
    DEFAULT_RUBRIC_PATH,
    LLMJudgeVeto,
    create_veto_from_policy,
)
from tools.certification.safety.veto_orchestrator import VetoOrchestrator


ARTIFACT_ROOT = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime"
POLICY_PATH = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_veto_policy.json"


def _seed_cache(namespace: str, query_text: str, cached_query: str, cached_answer: str) -> bool:
    try:
        from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
            SemanticCacheManager,
        )
    except ImportError:
        return False
    try:
        cache = SemanticCacheManager.get_instance()
    except Exception:
        return False
    payload = {"text": cached_answer, "answer": cached_answer,
               "cached_query_text": cached_query, "embedding_model_id": ""}
    context = json.dumps(
        {"body_text": query_text, "namespace": namespace, "tenant_id": "",
         "policy_hash": "no-policy"},
        sort_keys=True, separators=(",", ":"),
    )
    try:
        cache.learn(context, namespace, payload)
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────
# Orchestrator factories
# ─────────────────────────────────────────────────────────────────────


def _policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def _build_c_primary_fail_closed_orchestrator() -> VetoOrchestrator:
    """Policy-configured real LLMJudgeVeto. If the configured provider is
    unreachable the run times out / errors out → BLOCK. This is the
    fail-closed leg."""
    return VetoOrchestrator(stages=[create_veto_from_policy(_policy())])


def _build_c_primary_allow_orchestrator() -> tuple[VetoOrchestrator | None, str]:
    """Pick the first available approved SAFE-producing provider.

    W2b SSOT order (plan § 1):
      1. ``local_qwen`` if vLLM at localhost:8000 is reachable
      2. ``anthropic_haiku`` if ``ANTHROPIC_API_KEY`` is set

    ``mock_safe`` is **never** returned from this ladder. It remains
    behind LLMJUDGEVETO_APPROVED_MOCK_SAFE strictly for unit-test use.

    Returns (orchestrator, provider_used). If neither approved provider
    is available the orchestrator is ``None`` and the caller treats the
    allow leg as INFRASTRUCTURE_GAP without attempting a run.
    """
    # 1. local_qwen — model_id is discovered at runtime from /v1/models
    # so the attestation binds the actually-serving model. NEVER hardcode.
    qwen_stage = LLMJudgeVeto(provider="local_qwen",
                              rubric_path=DEFAULT_RUBRIC_PATH)
    if qwen_stage.is_available():
        return VetoOrchestrator(stages=[qwen_stage]), "local_qwen"
    # 2. anthropic_haiku — model_id pinned inside LLMJudgeVeto per provider
    # default (claude-3-haiku-20240307); no probe-side hardcoding needed.
    if os.environ.get("ANTHROPIC_API_KEY"):
        anthropic_stage = LLMJudgeVeto(provider="anthropic_haiku",
                                       rubric_path=DEFAULT_RUBRIC_PATH)
        return VetoOrchestrator(stages=[anthropic_stage]), "anthropic_haiku"
    # Neither available.
    return None, "NONE_AVAILABLE"


def _build_structural_orchestrator(query: str, cached: str) -> VetoOrchestrator:
    stage = DeterministicProofStage(
        verdicts={(query, cached): "SAFE"}, default="UNCERTAIN",
    )
    return VetoOrchestrator(stages=[stage])


def _run(run_dir: Path, orchestrator: VetoOrchestrator, user_query: str,
         namespace: str) -> Any:
    raw = {"transport": "api", "method": "POST",
           "content_type": "application/json", "source_channel": "rest_v2",
           "user_id": "u-w2-probe",
           "auth_credential": {"kind": "api_key", "token": "tok-w2"},
           "body_text": user_query}
    return run_integrated_safe_reuse(
        raw, namespace=namespace, tenant_id="", artifact_dir=run_dir,
        veto_orchestrator=orchestrator,
    )


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────


def main() -> int:
    print(f"[probe_integrated_runtime] entry point: {PRODUCER_COMPONENT}")
    os.environ.setdefault("SEMANTIC_CACHE_D2_ENABLED", "1")

    namespace = "w2_safe_reuse_proof"
    user_query = "What is the capital of France?"
    cached_query = "Tell me the capital of France."
    cached_answer = "The capital of France is Paris."
    seeded = _seed_cache(namespace, user_query, cached_query, cached_answer)
    print(f"[probe_integrated_runtime] cache seeded: {seeded}")

    # ── 1. c_primary_allow ────────────────────────────────────────
    allow_dir = ARTIFACT_ROOT / "c_primary_allow"
    if allow_dir.exists():
        shutil.rmtree(allow_dir)
    allow_orch, allow_provider = _build_c_primary_allow_orchestrator()
    print(f"[probe_integrated_runtime] [c_primary_allow] provider={allow_provider}")

    a = None
    a_match = "UNAVAILABLE"
    a_det = False
    a_allow = False
    a_x3 = None
    a_invoke_count = 0
    attestation_written = False
    attestation_path_rel: str | None = None

    if allow_orch is not None:
        a = _run(allow_dir, allow_orch, user_query, namespace)
        a_manifest = json.loads(
            (allow_dir / "integrated_runtime_artifact_manifest.json").read_text(encoding="utf-8"))
        a_match = a_manifest["payload"]["veto_stage_match_status"]
        a_det = a_manifest["payload"]["deterministic_proof_stage_used"]
        a_allow = a_manifest["payload"]["safe_reuse_allow"]
        a_x3 = a.x3_disposition
        a_invoke_count = a_manifest["payload"].get("llm_judge_invocation_count", 0)
        print(f"[probe_integrated_runtime] [c_primary_allow] match_status={a_match} "
              f"det_used={a_det} allow={a_allow} x3={a_x3} "
              f"outcome={a.gate_verdict_bundle.veto_outcome.value}")

        # Attestation — written only when the allow run actually succeeded
        # AND the provider is approved. No mock_safe path ever reaches here.
        allow_succeeded = (
            a_match == "PASS" and not a_det and a_allow is True and a_x3 == "X3D"
        )
        if allow_succeeded and allow_provider in APPROVED_PROVIDERS:
            veto_provenance = a_manifest["payload"].get("veto_provenance", {}) or {}
            # Bind the actual model the endpoint served during this run —
            # NEVER a hardcoded string. The veto stage captures
            # `resolved_model_id` (what was sent in the request body) and
            # `advertised_model_id` (what /v1/models reported) into its
            # result metadata; the manifest propagates them into
            # `veto_provenance`. A later composer / verifier layer flags
            # any mismatch via REJECT_MODEL_ID_MISMATCH.
            model_id = (
                veto_provenance.get("veto_model_id")
                or veto_provenance.get("model_id")
                or ""
            )
            if not model_id:
                raise RuntimeError(
                    "veto_provenance missing model_id — cannot build a valid "
                    "attestation without binding the actual model used. "
                    "Check LLMJudgeVeto.resolved_model_id wiring."
                )
            attestation_payload = build_attestation_payload(
                provider=allow_provider,
                model_id=model_id,
                model_version=veto_provenance.get("model_version") or model_id,
                rubric_path=DEFAULT_RUBRIC_PATH,
                raw_response=str(veto_provenance.get("raw_response", "")),
                response_hash_mode="paraphrase_tolerant",
                verdict="SAFE",
                confidence=float(veto_provenance.get("confidence", 0.0) or 0.0),
                latency_ms=float(veto_provenance.get("latency_ms", 0.0) or 0.0),
                llm_judge_invocation_count=a_invoke_count,
                veto_stage_class="LLMJudgeVeto",
                deterministic_proof_stage_used=False,
                x3_disposition=a_x3,
                safe_reuse_allow=True,
            )
            ap = write_attestation(allow_dir, attestation_payload)
            attestation_written = True
            attestation_path_rel = str(ap.relative_to(REPO_ROOT))
            print(f"[probe_integrated_runtime] attestation written: {attestation_path_rel}")
    else:
        print("[probe_integrated_runtime] [c_primary_allow] no approved provider "
              "available — INFRASTRUCTURE_GAP (honest non-green)")
        # Ensure the dir exists so downstream tooling finds a placeholder
        allow_dir.mkdir(parents=True, exist_ok=True)

    # ── 2. c_primary_fail_closed ─────────────────────────────────
    fc_dir = ARTIFACT_ROOT / "c_primary_fail_closed"
    if fc_dir.exists():
        shutil.rmtree(fc_dir)
    f = _run(fc_dir, _build_c_primary_fail_closed_orchestrator(),
             user_query, namespace)
    f_manifest = json.loads(
        (fc_dir / "integrated_runtime_artifact_manifest.json").read_text(encoding="utf-8"))
    f_match = f_manifest["payload"]["veto_stage_match_status"]
    f_det = f_manifest["payload"]["deterministic_proof_stage_used"]
    f_counters = f_manifest["payload"]["veto_counters"]
    print(f"[probe_integrated_runtime] [c_primary_fail_closed] match_status={f_match} "
          f"det_used={f_det} allow={f.safe_reuse_decision.allow} "
          f"x3={f.x3_disposition} outcome={f.gate_verdict_bundle.veto_outcome.value}")

    # ── 3. structural_allow_topology ─────────────────────────────
    s_dir = ARTIFACT_ROOT / "structural_allow_topology"
    if s_dir.exists():
        shutil.rmtree(s_dir)
    s = _run(s_dir, _build_structural_orchestrator(user_query, cached_query),
             user_query, namespace)
    s_manifest = json.loads(
        (s_dir / "integrated_runtime_artifact_manifest.json").read_text(encoding="utf-8"))
    s_match = s_manifest["payload"]["veto_stage_match_status"]
    print(f"[probe_integrated_runtime] [structural] match_status={s_match} "
          f"allow={s.safe_reuse_decision.allow} x3={s.x3_disposition}")

    # ── 4. latest/ mirrors c_primary_allow (canonical acceptance) ─
    latest = ARTIFACT_ROOT / "latest"
    if latest.exists() and latest.is_dir():
        shutil.rmtree(latest)
    if allow_dir.exists() and any(allow_dir.iterdir()):
        shutil.copytree(allow_dir, latest)

    # ── 5. Path-proof classification ledger ──────────────────────
    #   ALLOW path PASS requires: match_status=PASS + det_used=False
    #                             + allow=True + x3=X3D + attestation written
    #                             + provider in APPROVED_PROVIDERS
    #   FAIL-CLOSED path PASS requires: match_status=PASS + det_used=False
    #                             + allow=False + fail_closed_count>=1
    allow_pass = (
        a is not None
        and a_match == "PASS" and not a_det and a_allow is True
        and a_x3 == "X3D"
        and attestation_written
        and allow_provider in APPROVED_PROVIDERS
    )
    fc_pass = (f_match == "PASS" and not f_det
               and f.safe_reuse_decision.allow is False
               and int(f_counters.get("fail_closed_count", 0)) >= 1)

    path_proofs = {
        "schema_version": 2,
        "c_primary_allow": {
            "dir": str(allow_dir.relative_to(REPO_ROOT)),
            "provider_attempted": allow_provider,
            "match_status": a_match,
            "deterministic_proof_stage_used": a_det,
            "safe_reuse_allow": a_allow,
            "x3_disposition": a_x3,
            "llm_judge_invocation_count": a_invoke_count,
            "attestation_written": attestation_written,
            "attestation_path": attestation_path_rel,
            "pass": allow_pass,
            "infrastructure_gap_reason": (
                f"no live approved SAFE-producing provider available "
                f"(tried={allow_provider}). For RTC-REQ-056 certification "
                "acceptance, a LIVE approved provider is required: "
                "local_qwen at localhost:8000, OR set ANTHROPIC_API_KEY for "
                "anthropic_haiku. mock_safe is MOCK_PROVIDER_ONLY and is "
                "NEVER authorized for final certification acceptance."
            ) if not allow_pass else "",
        },
        "c_primary_fail_closed": {
            "dir": str(fc_dir.relative_to(REPO_ROOT)),
            "match_status": f_match,
            "deterministic_proof_stage_used": f_det,
            "safe_reuse_allow": f.safe_reuse_decision.allow,
            "x3_disposition": f.x3_disposition,
            "veto_counters": f_counters,
            "pass": fc_pass,
        },
        "structural_allow_topology": {
            "dir": str(s_dir.relative_to(REPO_ROOT)),
            "match_status": s_match,
            "safe_reuse_allow": s.safe_reuse_decision.allow,
            "x3_disposition": s.x3_disposition,
            "note": "STRUCTURAL_ONLY — documents ALLOW topology; "
                    "NEVER certifies RTC-REQ-056.",
        },
    }
    (ARTIFACT_ROOT / "path_proofs_ledger.json").write_text(
        json.dumps(path_proofs, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[probe_integrated_runtime] path_proofs_ledger written")
    print(f"[probe_integrated_runtime] allow_pass={allow_pass} fc_pass={fc_pass}")
    if not allow_pass:
        print(f"[probe_integrated_runtime] ALLOW path gap: "
              f"{path_proofs['c_primary_allow']['infrastructure_gap_reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
