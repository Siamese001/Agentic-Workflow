"""W2 — Integrated-runtime safe-reuse probe (dual-run: c_primary + structural).

This probe is the ONLY harness for the W2 evidence chain. It MUST NOT
call any layer-internal API directly (L0 cache lookup, L1 bridge, L2,
veto orchestrator, exit pipeline, L4, L6). It MUST call only:

    agentic_core.runtime.entrypoints.integrated_safe_reuse_run.run_integrated_safe_reuse(...)

Two runs are produced per invocation (W2 proof-hardening):

1. **c_primary** — uses the approved ``LLMJudgeVeto`` stage from
   ``tools.certification.safety.llm_judge_veto`` (built via
   ``create_veto_from_policy`` against the approved policy file). The
   configured provider may be ``mock`` in CI, which returns UNCERTAIN
   and drives the fail-closed UNKNOWN path — proving the C-primary
   integration end-to-end. Output dir: ``.../c_primary/`` AND mirrored
   to ``.../latest/``. This is the CANONICAL acceptance run.

2. **structural** — uses ``DeterministicProofStage`` returning SAFE for
   the seeded pair, so the ALLOW topology (X3D, terminal cache reuse)
   emits all 12 artifacts. Output dir: ``.../structural/``.
   ``veto_stage_match_status = STRUCTURAL_ONLY`` on this run — the
   composer refuses to accept it on its own.

Composer rule (see ``scripts/compose_semantic_cache_subclaims.py``):
``R1B_INTEGRATED_RUNTIME_PROOF = PASS`` ONLY when ``./latest/`` carries
``veto_stage_match_status == "PASS"`` AND all 5 verifiers exit 0.
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
from tools.certification.safety.llm_judge_veto import create_veto_from_policy
from tools.certification.safety.veto_orchestrator import VetoOrchestrator


ARTIFACT_ROOT = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime"
POLICY_PATH = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_veto_policy.json"


# ─────────────────────────────────────────────────────────────────────
# Cache pre-seeding (production-real, no mocks)
# ─────────────────────────────────────────────────────────────────────


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
    payload = {
        "text": cached_answer, "answer": cached_answer,
        "cached_query_text": cached_query, "embedding_model_id": "",
    }
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


def _build_c_primary_orchestrator() -> VetoOrchestrator:
    """Build the CANONICAL C-primary orchestrator: real LLMJudgeVeto from
    the approved policy file. Provider is whatever the policy names
    (``mock`` in CI; would be ``anthropic_haiku`` or ``local_qwen`` in
    live deployments)."""
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    stage = create_veto_from_policy(policy)
    return VetoOrchestrator(stages=[stage])


def _build_structural_orchestrator(query: str, cached: str) -> VetoOrchestrator:
    stage = DeterministicProofStage(
        verdicts={(query, cached): "SAFE"},
        default="UNCERTAIN",
    )
    return VetoOrchestrator(stages=[stage])


def _run_scenario(
    *, run_dir: Path, orchestrator: VetoOrchestrator,
    user_query: str, namespace: str,
) -> Any:
    raw_request: dict[str, Any] = {
        "transport": "api", "method": "POST",
        "content_type": "application/json", "source_channel": "rest_v2",
        "user_id": "u-w2-probe",
        "auth_credential": {"kind": "api_key", "token": "tok-w2"},
        "body_text": user_query,
    }
    return run_integrated_safe_reuse(
        raw_request, namespace=namespace, tenant_id="",
        artifact_dir=run_dir, veto_orchestrator=orchestrator,
    )


# ─────────────────────────────────────────────────────────────────────
# Run
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

    ts = int(time.time())

    # ── 1. C-primary (canonical) run ─────────────────────────────
    c_dir = ARTIFACT_ROOT / "c_primary"
    if c_dir.exists():
        shutil.rmtree(c_dir)
    c_result = _run_scenario(
        run_dir=c_dir,
        orchestrator=_build_c_primary_orchestrator(),
        user_query=user_query, namespace=namespace,
    )
    print(f"[probe_integrated_runtime] [c_primary] cache_hit={c_result.cache_hit}")
    print(f"[probe_integrated_runtime] [c_primary] safe_reuse.allow={c_result.safe_reuse_decision.allow}")
    print(f"[probe_integrated_runtime] [c_primary] reason_code={c_result.safe_reuse_decision.reason_code}")
    print(f"[probe_integrated_runtime] [c_primary] veto_outcome={c_result.gate_verdict_bundle.veto_outcome.value}")
    print(f"[probe_integrated_runtime] [c_primary] x3={c_result.x3_disposition}")

    # ── 2. Structural (subordinate) run ──────────────────────────
    s_dir = ARTIFACT_ROOT / "structural"
    if s_dir.exists():
        shutil.rmtree(s_dir)
    s_result = _run_scenario(
        run_dir=s_dir,
        orchestrator=_build_structural_orchestrator(user_query, cached_query),
        user_query=user_query, namespace=namespace,
    )
    print(f"[probe_integrated_runtime] [structural] cache_hit={s_result.cache_hit}")
    print(f"[probe_integrated_runtime] [structural] safe_reuse.allow={s_result.safe_reuse_decision.allow}")
    print(f"[probe_integrated_runtime] [structural] x3={s_result.x3_disposition}")

    # ── 3. Mirror c_primary → latest/ (canonical acceptance run) ─
    latest = ARTIFACT_ROOT / "latest"
    if latest.exists() and latest.is_dir():
        shutil.rmtree(latest)
    shutil.copytree(c_dir, latest)
    print(f"[probe_integrated_runtime] latest/ <- c_primary/ (canonical)")

    # ── 4. Quick classification summary (composer reads these) ───
    manifest = json.loads((latest / "integrated_runtime_artifact_manifest.json").read_text(encoding="utf-8"))
    p = manifest["payload"]
    print(f"[probe_integrated_runtime] latest.veto_stage_match_status={p['veto_stage_match_status']}")
    print(f"[probe_integrated_runtime] latest.deterministic_proof_stage_used={p['deterministic_proof_stage_used']}")
    print(f"[probe_integrated_runtime] latest.veto_provider={p['veto_provider']} model={p['veto_model_id']}")
    print(f"[probe_integrated_runtime] latest.llm_judge_invocation_count={p['llm_judge_invocation_count']}")
    print(f"[probe_integrated_runtime] latest.veto_counters={p['veto_counters']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
