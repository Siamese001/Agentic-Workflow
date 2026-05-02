"""R3_GROUNDED_READ — integrated runtime entrypoint.

Mirror of UWG_BLOCK/UWG_COMMIT entrypoints but drives a real retrieval
over an in-memory corpus and emits a typed FinalEvidenceContract. W4.1
closure of plan fortknox-100pct-static-runtime-gap-9a3d4f §GAP-6a.

The "real" substrate here is a minimal but non-mock retrieval pipeline:

  1. In-memory corpus of 3 fixed documents (the substrate must be
     deterministic and reproducible for signature-verified bundle
     reproducibility).
  2. Tokenize the query + each document (lowercase, alphanumeric split).
  3. Lexical overlap scoring (Jaccard over token sets) — not a mock, a
     real scoring function with deterministic output.
  4. Rank + select top-k (k=2 default).
  5. For each selected chunk, compute payload_sha256 of the chunk text.
  6. Emit FinalEvidenceContract with evidence_refs carrying chunk_ref +
     payload_sha256 + relevance_score.

The scoring is intentionally lexical, not neural — the goal is NOT
production retrieval quality, it is a REAL retriever (one whose output
is deterministically derivable from the input without any stubbed field).
Neural rerank is out of scope for W4.1 per the plan.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

from agentic_core.runtime.artifacts.integrated_runtime_emitter import (
    compute_artifact_hash,
)
from agentic_core.runtime.entrypoints.integrated_safe_reuse_run import (
    run_integrated_safe_reuse,
    IntegratedRunResult,
)


CHAIN_KIND = "R3_GROUNDED_READ"
ROUTE_FAMILY = "R3_GROUNDED_READ"

CORPUS_MANIFEST_FILENAME = "retrieval_corpus_manifest.json"
FINAL_EVIDENCE_CONTRACT_FILENAME = "final_evidence_contract.json"

_PRODUCER_COMPONENT = "agentic_core.runtime.entrypoints.integrated_grounded_read_run"
_PRODUCER_FUNCTION = "run_integrated_grounded_read"


# Deterministic in-memory corpus. Change this to a real vector store in
# future iterations; for W4.1 this is the substrate.
_CORPUS: tuple[dict[str, str], ...] = (
    {
        "chunk_id": "chunk::arch::001",
        "title": "Agentic-Workflow L7_AUDITABILITY plane",
        "text": (
            "The L7 auditability plane emits HOW traces, route-family "
            "coverage matrices, and Fort Knox per-req evidence rows for "
            "every certified integrated runtime chain. Each chain carries "
            "its own run_id, request_id, and trace_root identity."
        ),
    },
    {
        "chunk_id": "chunk::uwg::002",
        "title": "DurableWriteGateway commit pipeline",
        "text": (
            "DurableWriteGateway is the only admission gateway for durable "
            "L4 state mutations. CommitRequests must carry source_surface="
            "Exit; any other surface is rejected with a blocked-commit "
            "receipt. Successful commits emit UWGCommitReceipt with "
            "snapshot_before and snapshot_after bound to the audit ledger."
        ),
    },
    {
        "chunk_id": "chunk::retrieval::003",
        "title": "Retrieval evidence binding",
        "text": (
            "Grounded-read paths must bind their retrieved evidence via a "
            "FinalEvidenceContract. Each evidence_ref carries a chunk_ref, "
            "a payload_sha256, and a relevance_score. Support status "
            "reflects whether the retrieved chunks strongly, weakly, or "
            "do not support the claim under review."
        ),
    },
)


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_extra_envelope(
    path: Path, *, payload: dict[str, Any], upstream_hash: str = ""
) -> str:
    artifact_hash = compute_artifact_hash(payload)
    envelope = {
        "producer_component": _PRODUCER_COMPONENT,
        "producer_module": "integrated_grounded_read_run",
        "producer_function_or_class": _PRODUCER_FUNCTION,
        "emitted_at": _utc_now_iso(),
        "artifact_hash": artifact_hash,
        "upstream_artifact_ref": upstream_hash,
        "payload": payload,
    }
    path.write_text(
        json.dumps(envelope, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact_hash


def _restamp_envelope(path: Path) -> str:
    env = _read_json(path)
    payload = env.get("payload", {}) if isinstance(env, dict) else {}
    new_hash = compute_artifact_hash(payload)
    env["artifact_hash"] = new_hash
    path.write_text(
        json.dumps(env, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return new_hash


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _retrieve(query: str, *, top_k: int = 2) -> list[dict[str, Any]]:
    """Real lexical retrieval over the in-memory corpus. Deterministic."""
    q_toks = _tokenize(query)
    scored: list[tuple[float, dict[str, str]]] = []
    for chunk in _CORPUS:
        score = _jaccard(q_toks, _tokenize(chunk["title"] + " " + chunk["text"]))
        scored.append((score, chunk))
    scored.sort(key=lambda p: (-p[0], p[1]["chunk_id"]))
    out: list[dict[str, Any]] = []
    for score, chunk in scored[:top_k]:
        text_bytes = chunk["text"].encode("utf-8")
        out.append(
            {
                "chunk_ref": chunk["chunk_id"],
                "title": chunk["title"],
                "payload_sha256": hashlib.sha256(text_bytes).hexdigest(),
                "relevance_score": round(score, 6),
                "support_status": (
                    "strong" if score >= 0.15
                    else ("bounded" if score >= 0.05 else "weak")
                ),
            }
        )
    return out


def _corpus_manifest_payload() -> dict[str, Any]:
    """Deterministic description of the corpus. Reproducible sha256."""
    chunks = []
    for c in _CORPUS:
        chunks.append(
            {
                "chunk_id": c["chunk_id"],
                "title": c["title"],
                "payload_sha256": hashlib.sha256(c["text"].encode("utf-8")).hexdigest(),
                "byte_length": len(c["text"].encode("utf-8")),
            }
        )
    return {
        "corpus_version": "r3-inmem-v1",
        "corpus_size": len(_CORPUS),
        "retrieval_algorithm": "jaccard_over_alphanumeric_token_sets",
        "retrieval_deterministic": True,
        "chunks": chunks,
    }


def run_integrated_grounded_read(
    raw_request: dict[str, Any],
    *,
    namespace: str,
    tenant_id: str = "t:r3-grounded-read-run",
    artifact_dir: Path | str,
    query: str = "what does the L7 auditability plane emit",
    top_k: int = 2,
    veto_orchestrator: Any | None = None,
) -> IntegratedRunResult:
    """Drive an integrated R3_GROUNDED_READ chain end-to-end.

    Emits two family extras:
      - retrieval_corpus_manifest.json — deterministic corpus description
      - final_evidence_contract.json — typed FinalEvidenceContract with
        evidence_refs from the real retriever
    """
    art = Path(artifact_dir)
    art.mkdir(parents=True, exist_ok=True)

    # 1. Run the chain with chain_kind=R3_GROUNDED_READ.
    result = run_integrated_safe_reuse(
        raw_request,
        namespace=namespace,
        tenant_id=tenant_id,
        artifact_dir=art,
        veto_orchestrator=veto_orchestrator,
        chain_kind=CHAIN_KIND,
        route_family_override=ROUTE_FAMILY,
        extra_route_contract_fields={
            "route_family_proof_class": "REAL_RUNTIME",
            "r3_grounded_read_retrieval_algorithm": "jaccard_over_alphanumeric_token_sets",
            "r3_grounded_read_top_k": top_k,
        },
    )

    # 2. Identity from chain envelope.
    rie_env = _read_json(art / "runtime_identity_envelope.json")
    rie_payload = rie_env.get("payload", {}) if isinstance(rie_env, dict) else {}
    request_id = str(rie_payload.get("request_id") or rie_env.get("request_id") or "")
    trace_root = str(rie_payload.get("trace_root") or rie_env.get("trace_root") or "")

    # 3. Emit corpus manifest.
    corpus_payload = _corpus_manifest_payload()
    corpus_payload["run_id"] = result.run_id
    corpus_payload["request_id"] = request_id
    corpus_payload["trace_root"] = trace_root
    corpus_sha = _write_extra_envelope(
        art / CORPUS_MANIFEST_FILENAME, payload=corpus_payload
    )

    # 4. Drive the real retriever.
    evidence_refs = _retrieve(query, top_k=top_k)
    has_strong_support = any(ref["support_status"] == "strong" for ref in evidence_refs)

    # 5. Emit typed FinalEvidenceContract.
    fec_payload = {
        "final_evidence_contract_id": f"fec::r3::{result.run_id}",
        "schema_version": "1.0.0",
        "query_text": query,
        "evidence_refs": evidence_refs,
        "evidence_ref_count": len(evidence_refs),
        "has_strong_support": has_strong_support,
        "retrieval_algorithm": "jaccard_over_alphanumeric_token_sets",
        "corpus_version": "r3-inmem-v1",
        "corpus_manifest_sha256": corpus_sha,
        "run_id": result.run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "integrated_runtime_origin": True,
        "produced_by": _PRODUCER_COMPONENT + "." + _PRODUCER_FUNCTION,
    }
    fec_sha = _write_extra_envelope(
        art / FINAL_EVIDENCE_CONTRACT_FILENAME,
        payload=fec_payload,
        upstream_hash=corpus_sha,
    )

    # 6. Cascade manifest + spine.
    manifest_path = art / "integrated_runtime_artifact_manifest.json"
    manifest_env = _read_json(manifest_path)
    manifest_payload = manifest_env.get("payload", {})
    new_manifest_hash = ""
    if isinstance(manifest_payload, dict):
        manifest_payload["retrieval_corpus_manifest_ref"] = (
            f"artifact://{CORPUS_MANIFEST_FILENAME}"
        )
        manifest_payload["retrieval_corpus_manifest_sha256"] = corpus_sha
        manifest_payload["final_evidence_contract_ref"] = (
            f"artifact://{FINAL_EVIDENCE_CONTRACT_FILENAME}"
        )
        manifest_payload["final_evidence_contract_sha256"] = fec_sha
        manifest_payload["r3_evidence_ref_count"] = len(evidence_refs)
        manifest_path.write_text(
            json.dumps(manifest_env, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        new_manifest_hash = _restamp_envelope(manifest_path)

    nhsr_path = art / "no_harness_stamp_receipt.json"
    nhsr_env = _read_json(nhsr_path)
    if isinstance(nhsr_env, dict) and new_manifest_hash:
        nhsr_env["upstream_artifact_ref"] = new_manifest_hash
        nhsr_path.write_text(
            json.dumps(nhsr_env, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        new_nhsr_hash = _restamp_envelope(nhsr_path)
    else:
        new_nhsr_hash = nhsr_env.get("artifact_hash", "") if isinstance(nhsr_env, dict) else ""

    spine_path = art / "agentic_core_spine_proof.json"
    spine_env = _read_json(spine_path)
    spine_payload = spine_env.get("payload", {})
    if isinstance(spine_payload, dict):
        spine_payload["final_evidence_contract_sha256"] = fec_sha
        spine_payload["retrieval_corpus_manifest_sha256"] = corpus_sha
        spine_payload["r3_evidence_ref_count"] = len(evidence_refs)
        spine_payload["r3_has_strong_support"] = has_strong_support
        if new_manifest_hash:
            spine_payload["artifact_manifest_ref"] = new_manifest_hash
        if new_nhsr_hash:
            spine_env["upstream_artifact_ref"] = new_nhsr_hash
        spine_path.write_text(
            json.dumps(spine_env, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _restamp_envelope(spine_path)

    return result


__all__ = [
    "run_integrated_grounded_read",
    "CHAIN_KIND",
    "ROUTE_FAMILY",
    "CORPUS_MANIFEST_FILENAME",
    "FINAL_EVIDENCE_CONTRACT_FILENAME",
]
