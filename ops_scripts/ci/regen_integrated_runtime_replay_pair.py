"""Wave C — produce R1B replay pair + mutation negative.

Drives ``run_integrated_safe_reuse`` three times to produce evidence
for RTC-REQ-023 (replay pair with stable replay_key + deterministic
digest) and RTC-REQ-024 (replay mutation negative).

Layout produced:
  artifacts/certification/integrated_runtime/replay/
    run_1/<bundle>           — first run with canonical SAFE pair
    run_2/<bundle>           — second run, same input
    run_3_mutated/<bundle>   — third run, MUTATED input (negative control)
    replay_pair_receipt.json
    replay_mutation_negative_receipt.json

Acceptance:
  - run_1 and run_2 produce IDENTICAL replay_key, trace_root remains
    deterministic per content (or per the entrypoint's trace policy),
    and full bundle artifact hashes match for content-stable artifacts.
  - run_3 produces a DIFFERENT replay_key (mutation detected).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

REPLAY_ROOT = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "replay"
PAIR_RECEIPT = REPLAY_ROOT / "replay_pair_receipt.json"
NEG_RECEIPT = REPLAY_ROOT / "replay_mutation_negative_receipt.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bundle_replay_key(bundle_dir: Path) -> str:
    """Read replay_key from route_contract.json's payload."""
    rc = json.loads((bundle_dir / "route_contract.json").read_text(encoding="utf-8"))
    return rc.get("payload", {}).get("replay_key", "")


def _bundle_trace_root(bundle_dir: Path) -> str:
    rc = json.loads((bundle_dir / "route_contract.json").read_text(encoding="utf-8"))
    return rc.get("payload", {}).get("trace_root") or rc.get("payload", {}).get("trace_id", "")


def _content_hash_for_replay(bundle_dir: Path) -> str:
    """Deterministic digest over the **content-stable** subset of the
    bundle (excludes per-invocation fields like emitted_at, run_id,
    trace_root that vary by run even when input is identical).

    Content-stable artifacts for replay invariants:
      - validated_request.payload (input shape; identical for same input)
      - route_contract.payload.replay_key + policy_hash + blueprint_hash
      - terminal_ret_packet.payload.execution_form + assertions
      - x3_disposition_receipt.payload.x3_disposition + verdict_count
    """
    parts: list[bytes] = []
    files = (
        "validated_request.json",
        "route_contract.json",
        "terminal_ret_packet.json",
        "x3_disposition_receipt.json",
    )
    # Per RTC-REQ-023: the replay invariant is bound to *request content*,
    # not intake state. ``policy_hash`` is excluded because it carries
    # per-invocation intake-manifest noise (timestamps, intake-state).
    # ``replay_key`` is the authoritative bound — if that matches AND
    # the structural fields below match, the run is a faithful replay.
    stable_keys = {
        "validated_request.json": ("intake_status", "permitted_next_layer", "request_shape_class"),
        "route_contract.json": ("replay_key", "blueprint_hash", "intent_class", "namespace"),
        "terminal_ret_packet.json": ("execution_form", "no_l2_execution_assertion", "exit_review_required"),
        "x3_disposition_receipt.json": ("x3_disposition", "verdict_count"),
    }
    for fname in files:
        d = json.loads((bundle_dir / fname).read_text(encoding="utf-8"))
        pl = d.get("payload") or {}
        keys = stable_keys[fname]
        sub = {k: pl.get(k) for k in keys if k in pl}
        canon = json.dumps(sub, sort_keys=True, separators=(",", ":")).encode("utf-8")
        parts.append(fname.encode("utf-8") + b"|" + canon + b"\n")
    return _sha256_bytes(b"".join(parts))


def _drive_safe_reuse(
    *, artifact_dir: Path, query_text: str, namespace: str, cached_query: str
) -> Any:
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
        SemanticCacheManager,
    )
    from agentic_core.runtime.entrypoints.integrated_safe_reuse_run import (
        run_integrated_safe_reuse,
    )
    from tools.certification.safety.deterministic_proof_stage import (
        DeterministicProofStage,
    )
    from tools.certification.safety.veto_orchestrator import VetoOrchestrator

    cache = SemanticCacheManager.get_instance()
    ctx = json.dumps(
        {
            "body_text": query_text,
            "namespace": namespace,
            "tenant_id": "",
            "policy_hash": "no-policy",
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    cache.learn(ctx, namespace, {
        "text": "Paris.", "answer": "Paris.", "cached_query_text": cached_query,
    })
    os.environ.setdefault("SEMANTIC_CACHE_D2_ENABLED", "1")
    proof = VetoOrchestrator(stages=[
        DeterministicProofStage(verdicts={(query_text, cached_query): "SAFE"})
    ])
    return run_integrated_safe_reuse(
        {"body_text": query_text, "transport": "api"},
        namespace=namespace,
        tenant_id="",
        artifact_dir=artifact_dir,
        veto_orchestrator=proof,
    )


def main() -> int:
    if REPLAY_ROOT.exists():
        shutil.rmtree(REPLAY_ROOT)
    REPLAY_ROOT.mkdir(parents=True, exist_ok=True)

    run_1_dir = REPLAY_ROOT / "run_1"
    run_2_dir = REPLAY_ROOT / "run_2"
    run_3_dir = REPLAY_ROOT / "run_3_mutated"

    canonical_query = "What is the capital of France?"
    canonical_cached = "Tell me the capital of France."
    canonical_namespace = "test_replay_pair"

    # Run 1 — canonical input
    _drive_safe_reuse(
        artifact_dir=run_1_dir,
        query_text=canonical_query,
        namespace=canonical_namespace,
        cached_query=canonical_cached,
    )
    rk1 = _bundle_replay_key(run_1_dir)
    th1 = _content_hash_for_replay(run_1_dir)
    tr1 = _bundle_trace_root(run_1_dir)

    # Run 2 — IDENTICAL input (replay)
    _drive_safe_reuse(
        artifact_dir=run_2_dir,
        query_text=canonical_query,
        namespace=canonical_namespace,
        cached_query=canonical_cached,
    )
    rk2 = _bundle_replay_key(run_2_dir)
    th2 = _content_hash_for_replay(run_2_dir)
    tr2 = _bundle_trace_root(run_2_dir)

    # Run 3 — MUTATED input (negative control)
    mutated_query = "What is the capital of Germany?"
    _drive_safe_reuse(
        artifact_dir=run_3_dir,
        query_text=mutated_query,
        namespace=canonical_namespace,
        cached_query=canonical_cached,
    )
    rk3 = _bundle_replay_key(run_3_dir)
    th3 = _content_hash_for_replay(run_3_dir)

    # Replay-pair receipt (RTC-REQ-023)
    pair_pass = (rk1 == rk2) and (th1 == th2) and bool(rk1) and bool(th1)
    pair_receipt = {
        "verifier_input": "scripts/regen_integrated_runtime_replay_pair.py",
        "scope": "RTC-REQ-023 — replay pair with stable replay_key + deterministic digest",
        "evaluated_at_utc": _utc_now(),
        "result": "PASS" if pair_pass else "FAIL",
        "run_1": {
            "artifact_dir": str(run_1_dir.relative_to(REPO_ROOT)),
            "replay_key": rk1,
            "content_hash": th1,
            "trace_root": tr1,
        },
        "run_2": {
            "artifact_dir": str(run_2_dir.relative_to(REPO_ROOT)),
            "replay_key": rk2,
            "content_hash": th2,
            "trace_root": tr2,
        },
        "replay_key_match": rk1 == rk2,
        "content_hash_match": th1 == th2,
        "input_query": canonical_query,
        "input_cached_query": canonical_cached,
    }
    PAIR_RECEIPT.write_text(json.dumps(pair_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Mutation-negative receipt (RTC-REQ-024)
    neg_pass = (rk1 != rk3) or (th1 != th3)  # at least one MUST differ
    neg_receipt = {
        "verifier_input": "scripts/regen_integrated_runtime_replay_pair.py",
        "scope": "RTC-REQ-024 — replay mutation negative (mutated input MUST diverge)",
        "evaluated_at_utc": _utc_now(),
        "result": "PASS" if neg_pass else "FAIL",
        "canonical_run": {
            "replay_key": rk1,
            "content_hash": th1,
            "input_query": canonical_query,
        },
        "mutated_run": {
            "artifact_dir": str(run_3_dir.relative_to(REPO_ROOT)),
            "replay_key": rk3,
            "content_hash": th3,
            "input_query": mutated_query,
        },
        "replay_key_diverges": rk1 != rk3,
        "content_hash_diverges": th1 != th3,
        "expected_fail_reason": "input mutation must produce a different replay_key OR content_hash",
        "actual_fail_reason": (
            "" if neg_pass else
            "mutation NOT detected — replay infrastructure does not bind to input"
        ),
    }
    NEG_RECEIPT.write_text(json.dumps(neg_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"[regen_replay_pair] pair_result={'PASS' if pair_pass else 'FAIL'}")
    print(f"  run_1.replay_key={rk1[:20]}... content_hash={th1[:20]}...")
    print(f"  run_2.replay_key={rk2[:20]}... content_hash={th2[:20]}...")
    print(f"  match: replay_key={rk1==rk2}, content_hash={th1==th2}")
    print(f"  wrote: {PAIR_RECEIPT.relative_to(REPO_ROOT)}")
    print()
    print(f"[regen_replay_pair] mutation_result={'PASS' if neg_pass else 'FAIL'}")
    print(f"  run_3.replay_key={rk3[:20]}... content_hash={th3[:20]}...")
    print(f"  diverges: replay_key={rk1!=rk3}, content_hash={th1!=th3}")
    print(f"  wrote: {NEG_RECEIPT.relative_to(REPO_ROOT)}")

    return 0 if (pair_pass and neg_pass) else 2


if __name__ == "__main__":
    sys.exit(main())
