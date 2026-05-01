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
from tools.certification.safety.deterministic_proof_stage import DeterministicProofStage
from tools.certification.safety.llm_judge_veto import (
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


def _build_c_primary_allow_orchestrator() -> tuple[VetoOrchestrator, str]:
    """Pick the first available SAFE-producing provider for LLMJudgeVeto.

    Order:
      1. ``anthropic_haiku`` if ``ANTHROPIC_API_KEY`` is set
      2. ``local_qwen`` if vLLM at localhost:8000 is reachable
      3. ``mock_safe`` if ``LLMJUDGEVETO_APPROVED_MOCK_SAFE=1``

    Returns (orchestrator, provider_used). If none available, the
    fallback is a ``mock_safe`` LLMJudgeVeto with ``is_available=False``
    — the probe will attempt evaluate() and log the gap honestly.
    """
    from pathlib import Path as _P
    rubric = _policy().get("llm_judge_config", {}).get(
        "rubric_path",
        "tools/certification/safety/rubrics/semantic_cache_equivalence_v1.yaml",
    )
    # 1. Anthropic
    if os.environ.get("ANTHROPIC_API_KEY"):
        stage = LLMJudgeVeto(provider="anthropic_haiku",
                             model_id="claude-haiku-4-5",
                             rubric_path=_P(rubric))
        return VetoOrchestrator(stages=[stage]), "anthropic_haiku"
    # 2. local_qwen (probe live)
    probe_stage = LLMJudgeVeto(provider="local_qwen",
                               model_id="Qwen2.5-7B-Instruct",
                               rubric_path=_P(rubric))
    if probe_stage.is_available():
        return VetoOrchestrator(stages=[probe_stage]), "local_qwen"
    # 3. approved mock_safe (opt-in)
    stage = LLMJudgeVeto(provider="mock_safe",
                         model_id="mock_safe",
                         rubric_path=_P(rubric))
    if stage.is_available():
        return VetoOrchestrator(stages=[stage]), "mock_safe"
    # 4. No provider — return a mock_safe stage that will answer SAFE
    #    anyway, BUT is_available=False means the probe records
    #    infrastructure_gap and the composer downgrades acceptance.
    return VetoOrchestrator(stages=[stage]), "NONE_AVAILABLE"


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
    a = _run(allow_dir, allow_orch, user_query, namespace)
    a_manifest = json.loads(
        (allow_dir / "integrated_runtime_artifact_manifest.json").read_text(encoding="utf-8"))
    a_match = a_manifest["payload"]["veto_stage_match_status"]
    a_det = a_manifest["payload"]["deterministic_proof_stage_used"]
    a_allow = a_manifest["payload"]["safe_reuse_allow"]
    print(f"[probe_integrated_runtime] [c_primary_allow] match_status={a_match} "
          f"det_used={a_det} allow={a_allow} x3={a.x3_disposition} "
          f"outcome={a.gate_verdict_bundle.veto_outcome.value}")

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
    shutil.copytree(allow_dir, latest)

    # ── 5. Path-proof classification ledger ──────────────────────
    #   ALLOW path PASS requires: match_status=PASS + det_used=False
    #                             + allow=True + x3=X3D
    #   FAIL-CLOSED path PASS requires: match_status=PASS + det_used=False
    #                             + allow=False + fail_closed_count>=1
    allow_pass = (a_match == "PASS" and not a_det and a_allow is True
                  and a.x3_disposition == "X3D")
    fc_pass = (f_match == "PASS" and not f_det
               and f.safe_reuse_decision.allow is False
               and int(f_counters.get("fail_closed_count", 0)) >= 1)

    path_proofs = {
        "schema_version": 1,
        "c_primary_allow": {
            "dir": str(allow_dir.relative_to(REPO_ROOT)),
            "provider_attempted": allow_provider,
            "match_status": a_match,
            "deterministic_proof_stage_used": a_det,
            "safe_reuse_allow": a_allow,
            "x3_disposition": a.x3_disposition,
            "llm_judge_invocation_count": a_manifest["payload"]["llm_judge_invocation_count"],
            "pass": allow_pass,
            "infrastructure_gap_reason": (
                f"no SAFE-producing provider available (tried={allow_provider}); "
                "set ANTHROPIC_API_KEY, run local_qwen at localhost:8000, OR set "
                "LLMJUDGEVETO_APPROVED_MOCK_SAFE=1 to use the approved mock."
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
