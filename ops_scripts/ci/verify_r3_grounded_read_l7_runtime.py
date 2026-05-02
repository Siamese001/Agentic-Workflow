"""R3_GROUNDED_READ integrated-runtime verifier — fail-closed.

Asserts that the R3 chain drove a real retrieval and emitted a typed
FinalEvidenceContract.

Fail codes: R3_WRONG_CHAIN_KIND, R3_WRONG_ROUTE_FAMILY, R3_FEC_MISSING,
R3_NOT_INTEGRATED, R3_NO_EVIDENCE_REFS, R3_REFS_MISSING_HASH,
R3_CORPUS_MISSING, R3_HOW_TRACE_WRONG_KIND, R3_FK_NOT_EMITTED,
R3_MANIFEST_NO_FEC_REF, R3_SPINE_NO_FEC_REF, R3_COVERAGE_NOT_CERTIFIED.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1]))

from _w2_verifier_common import detect_chain_kind, fail, passed, resolve_artifact_dir  # noqa: E402


def _read_payload(art: Path, fname: str) -> dict:
    p = art / fname
    if not p.exists():
        return {}
    try:
        env = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    payload = env.get("payload", {}) if isinstance(env, dict) else {}
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str]) -> int:
    art = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    kind = detect_chain_kind(art)
    print(f"[verify_r3_grounded_read_l7_runtime] artifact_dir={art} chain_kind={kind}")

    if kind != "R3_GROUNDED_READ":
        return fail("R3_WRONG_CHAIN_KIND", f"chain_kind={kind!r}; expected 'R3_GROUNDED_READ'")
    rc = _read_payload(art, "route_contract.json")
    if rc.get("route_family") != "R3_GROUNDED_READ":
        return fail("R3_WRONG_ROUTE_FAMILY", f"route_family={rc.get('route_family')!r}")

    fec = _read_payload(art, "final_evidence_contract.json")
    if not fec:
        return fail("R3_FEC_MISSING", "final_evidence_contract.json missing or empty")
    if not fec.get("integrated_runtime_origin"):
        return fail("R3_NOT_INTEGRATED", "FEC.integrated_runtime_origin != True")
    refs = fec.get("evidence_refs", [])
    if not refs:
        return fail("R3_NO_EVIDENCE_REFS", "FEC.evidence_refs is empty")
    for r in refs:
        if not isinstance(r, dict) or not r.get("payload_sha256") or not r.get("chunk_ref"):
            return fail(
                "R3_REFS_MISSING_HASH",
                f"evidence_ref missing chunk_ref or payload_sha256: {r}",
            )

    corpus = _read_payload(art, "retrieval_corpus_manifest.json")
    if not corpus:
        return fail("R3_CORPUS_MISSING", "retrieval_corpus_manifest.json missing")

    ht = _read_payload(art, "agentic_core_how_trace.json")
    if ht.get("chain_kind") != "R3_GROUNDED_READ":
        return fail("R3_HOW_TRACE_WRONG_KIND", f"how_trace.chain_kind={ht.get('chain_kind')!r}")

    fk_dir = art / "fortknox_l7_evidence"
    if not fk_dir.exists() or not any(fk_dir.iterdir()):
        return fail("R3_FK_NOT_EMITTED", "fortknox_l7_evidence/ missing")

    manifest = _read_payload(art, "integrated_runtime_artifact_manifest.json")
    if not manifest.get("final_evidence_contract_ref"):
        return fail("R3_MANIFEST_NO_FEC_REF", "manifest.final_evidence_contract_ref missing")
    spine = _read_payload(art, "agentic_core_spine_proof.json")
    if not spine.get("final_evidence_contract_sha256"):
        return fail("R3_SPINE_NO_FEC_REF", "spine.final_evidence_contract_sha256 missing")

    cov = _read_payload(art, "agentic_core_l7_route_family_coverage.json")
    fams = cov.get("route_families", [])
    row = next((f for f in fams if isinstance(f, dict) and f.get("route_family") == "R3_GROUNDED_READ"), None)
    if not row or row.get("certification_status") != "CERTIFIED" or row.get("proof_class") != "REAL_RUNTIME":
        return fail(
            "R3_COVERAGE_NOT_CERTIFIED",
            f"coverage R3 row={row!r}; expected CERTIFIED/REAL_RUNTIME",
        )

    return passed(
        f"R3_GROUNDED_READ valid (evidence_ref_count={len(refs)}, "
        f"corpus_size={corpus.get('corpus_size')}, coverage=CERTIFIED/REAL_RUNTIME)"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
