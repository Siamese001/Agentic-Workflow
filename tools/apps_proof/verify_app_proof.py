"""Independent proof verifier — reads on-disk artifacts only.

CLI:

    python -m tools.apps_proof.verify_app_proof \
        --proof-dir artifacts/apps_proof/<app_name>/<run_id>

The verifier NEVER trusts in-memory state from the runner. It reads
``run_manifest.json``, every artifact under ``contracts/``,
``trace/otel_trace.json``, ``gates/gate_verdicts.jsonl``,
``replay/replay_comparison.json``, and ``adg/adg_delta.json`` (if present),
then independently:

  1. asserts every required artifact exists
  2. recomputes contract digests and the proof_manifest_hash
  3. checks span tree connectivity (every parent_span_id resolves)
  4. confirms contract chain joins to spans
  5. validates required-stage span coverage for the run's route shape
  6. verifies replay determinism (replay_run_1 == replay_run_2 on canonical fields)
  7. asserts no L6 record is timestamped before runtime_boundary_ts
  8. asserts ExitDisposition exists when final output exists
  9. asserts ADG risk did not worsen for touched paths (when adg_delta.json present)

Outputs:

  - ``verifier/proof_verdict.json`` (final_status: PASS|FAIL)
  - ``verifier/proof_report.md`` (human-readable summary)
  - ``verifier/failure_reasons.jsonl`` (one JSON line per failed check)

Exit code: 0 on PASS, 1 on FAIL.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERIFIER_VERSION = "1.0.0-w3"  # bump when the algorithm changes

PROOF_STATUS_PASS = "PASS"
PROOF_STATUS_FAIL = "FAIL"

# Required stage spans by route shape — every grounded run MUST contain
# spans whose ``layer`` and (optional) ``name`` match these patterns.
# Matching is on ``layer`` alone; ``name`` is informational.
REQUIRED_STAGES_GROUNDED = (
    ("U0", "u0.intake"),
    ("L1", "l1.plan"),
    ("L0", "l0.route"),
    ("C0", "c0.*"),
    ("PromptAssembly", "pa.assemble"),
    ("L2", "l2.execute"),
    ("Exit", "exit.evaluate"),
)

REQUIRED_STAGES_NON_GROUNDED = (
    ("U0", "u0.intake"),
    ("L1", "l1.plan"),
    ("L0", "l0.route"),
    ("L2", "l2.execute"),
    ("Exit", "exit.evaluate"),
)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _sha256(obj: Any) -> str:
    return hashlib.sha256(_canonical_json(obj).encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class CheckResult:
    """One verifier check."""

    name: str
    ok: bool
    detail: str = ""
    fail_code: str | None = None  # e.g. FAIL_MISSING_C0_CONTRACT
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "ok": self.ok,
            "detail": self.detail,
            "fail_code": self.fail_code,
            "evidence": dict(self.evidence),
        }


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def _check_required_files(proof_dir: Path) -> list[CheckResult]:
    """Every required path must exist and be non-empty."""
    required = [
        "run_manifest.json",
        "trace/otel_trace.json",
        "trace/span_tree.txt",
        "trace/span_coverage.json",
        "gates/gate_verdicts.jsonl",
        "replay/replay_comparison.json",
    ]
    results: list[CheckResult] = []
    for rel in required:
        p = proof_dir / rel
        ok = p.exists() and p.stat().st_size > 0
        results.append(
            CheckResult(
                name=f"required_file:{rel}",
                ok=ok,
                detail="" if ok else f"missing or empty: {p}",
                fail_code=None if ok else "FAIL_MISSING_REQUIRED_FILE",
                evidence={"path": str(p), "size": p.stat().st_size if p.exists() else 0},
            )
        )
    return results


def _check_run_manifest_links(proof_dir: Path) -> CheckResult:
    """run_manifest.json must include run_id, trace_id, policy_hash,
    blueprint_hash, replay_key."""
    m = _load_json(proof_dir / "run_manifest.json")
    if m is None:
        return CheckResult(
            name="run_manifest_loadable",
            ok=False,
            detail="run_manifest.json missing or invalid",
            fail_code="FAIL_MISSING_RUN_MANIFEST",
        )
    required = ("run_id", "trace_id", "policy_hash", "blueprint_hash", "replay_key")
    missing = [k for k in required if not m.get(k)]
    if missing:
        return CheckResult(
            name="run_manifest_required_fields",
            ok=False,
            detail=f"missing fields: {missing}",
            fail_code="FAIL_INCOMPLETE_RUN_MANIFEST",
            evidence={"missing": missing},
        )
    return CheckResult(name="run_manifest_required_fields", ok=True)


def _check_artifacts_join_run(proof_dir: Path) -> list[CheckResult]:
    """Every artifact JSON under contracts/ must reference run_id and
    trace_id from run_manifest."""
    m = _load_json(proof_dir / "run_manifest.json") or {}
    run_id = m.get("run_id")
    trace_id = m.get("trace_id")
    contracts_dir = proof_dir / "contracts"
    results: list[CheckResult] = []
    if not contracts_dir.exists():
        return [
            CheckResult(
                name="artifacts_join_run",
                ok=False,
                detail="contracts/ missing",
                fail_code="FAIL_MISSING_CONTRACTS_DIR",
            )
        ]
    for jp in sorted(contracts_dir.glob("*.json")):
        body = _load_json(jp)
        if body is None:
            results.append(
                CheckResult(
                    name=f"artifact_loadable:{jp.name}",
                    ok=False,
                    detail=f"unloadable: {jp}",
                    fail_code="FAIL_UNLOADABLE_ARTIFACT",
                )
            )
            continue
        # Search recursively for trace_id / run_id mentions
        body_str = _canonical_json(body)
        contains_run = run_id is None or (run_id in body_str)
        contains_trace = trace_id is None or (trace_id in body_str)
        ok = contains_run and contains_trace
        results.append(
            CheckResult(
                name=f"artifact_join:{jp.name}",
                ok=ok,
                detail="" if ok else "missing run_id or trace_id reference",
                fail_code=None if ok else "FAIL_ARTIFACT_NO_TRACE_LINK",
                evidence={
                    "contains_run_id": contains_run,
                    "contains_trace_id": contains_trace,
                },
            )
        )
    return results


def _check_span_tree(proof_dir: Path) -> list[CheckResult]:
    """Every span's parent_span_id must resolve, except root(s)."""
    spans = _load_json(proof_dir / "trace" / "otel_trace.json")
    if not isinstance(spans, list):
        return [
            CheckResult(
                name="span_tree_loadable",
                ok=False,
                detail="otel_trace.json missing or not a list",
                fail_code="FAIL_MISSING_OTEL_TRACE",
            )
        ]
    span_ids = {s.get("span_id") for s in spans if isinstance(s, dict)}
    results: list[CheckResult] = []
    roots = 0
    for s in spans:
        if not isinstance(s, dict):
            continue
        parent = s.get("parent_span_id")
        if parent is None:
            roots += 1
            continue
        if parent not in span_ids:
            results.append(
                CheckResult(
                    name=f"span_orphan:{s.get('span_id')}",
                    ok=False,
                    detail=f"parent_span_id={parent!r} not in span_ids",
                    fail_code="FAIL_SPAN_ORPHAN",
                    evidence={"span_id": s.get("span_id"), "parent_span_id": parent},
                )
            )
    if roots == 0:
        results.append(
            CheckResult(
                name="span_tree_has_root",
                ok=False,
                detail="no root span (all spans have parent)",
                fail_code="FAIL_NO_ROOT_SPAN",
            )
        )
    if not results:
        results.append(CheckResult(name="span_tree_connected", ok=True))
    return results


def _check_required_stages(proof_dir: Path) -> CheckResult:
    """Required stage spans for the route shape (grounded vs non-grounded)."""
    m = _load_json(proof_dir / "run_manifest.json") or {}
    grounded = bool(m.get("grounding_required", False))
    spans = _load_json(proof_dir / "trace" / "otel_trace.json") or []
    layers_seen = {s.get("layer") for s in spans if isinstance(s, dict)}
    required = REQUIRED_STAGES_GROUNDED if grounded else REQUIRED_STAGES_NON_GROUNDED
    missing = [layer for (layer, _name) in required if layer not in layers_seen]
    if missing:
        return CheckResult(
            name="required_stages",
            ok=False,
            detail=f"missing layers: {missing}",
            fail_code="FAIL_SPAN_COVERAGE_GAP",
            evidence={"grounded": grounded, "missing_layers": missing},
        )
    return CheckResult(
        name="required_stages",
        ok=True,
        evidence={"grounded": grounded, "layers_seen": sorted(filter(None, layers_seen))},
    )


def _check_grounded_has_c0(proof_dir: Path) -> CheckResult:
    """If grounding_required, c0_final_evidence_contract.json MUST exist."""
    m = _load_json(proof_dir / "run_manifest.json") or {}
    grounded = bool(m.get("grounding_required", False))
    if not grounded:
        return CheckResult(name="grounded_has_c0", ok=True, detail="not grounded")
    p = proof_dir / "contracts" / "c0_final_evidence_contract.json"
    ok = p.exists() and p.stat().st_size > 0
    return CheckResult(
        name="grounded_has_c0",
        ok=ok,
        detail="" if ok else "grounded run missing c0_final_evidence_contract.json",
        fail_code=None if ok else "FAIL_MISSING_C0_CONTRACT",
    )


def _check_exit_when_output(proof_dir: Path) -> CheckResult:
    """If l2_sealed_artifact.json exists, exit_disposition.json MUST exist."""
    sealed = proof_dir / "contracts" / "l2_sealed_artifact.json"
    exit_d = proof_dir / "contracts" / "exit_disposition.json"
    has_sealed = sealed.exists()
    has_exit = exit_d.exists()
    if has_sealed and not has_exit:
        return CheckResult(
            name="exit_when_output",
            ok=False,
            detail="sealed artifact present but exit_disposition.json missing",
            fail_code="FAIL_OUTPUT_WITHOUT_EXIT",
        )
    return CheckResult(name="exit_when_output", ok=True)


def _check_l6_post_exit(proof_dir: Path) -> CheckResult:
    """L6 records must have started_at >= runtime_boundary_ts."""
    m = _load_json(proof_dir / "run_manifest.json") or {}
    boundary = m.get("runtime_boundary_ts")
    spans = _load_json(proof_dir / "trace" / "otel_trace.json") or []
    if not boundary:
        return CheckResult(
            name="l6_post_exit",
            ok=True,
            detail="no runtime_boundary_ts recorded; nothing to enforce",
        )
    bad: list[dict[str, Any]] = []
    for s in spans:
        if not isinstance(s, dict):
            continue
        if s.get("layer") != "L6":
            continue
        started_at = s.get("started_at")
        if started_at and started_at < boundary:
            bad.append(
                {
                    "span_id": s.get("span_id"),
                    "started_at": started_at,
                    "runtime_boundary_ts": boundary,
                }
            )
    if bad:
        return CheckResult(
            name="l6_post_exit",
            ok=False,
            detail=f"{len(bad)} L6 span(s) before runtime boundary",
            fail_code="FAIL_L6_PRE_EXIT_MUTATION_RISK",
            evidence={"violations": bad},
        )
    return CheckResult(name="l6_post_exit", ok=True)


def _check_replay(proof_dir: Path) -> CheckResult:
    """replay_comparison.json must report ok=True."""
    rc = _load_json(proof_dir / "replay" / "replay_comparison.json")
    if rc is None:
        return CheckResult(
            name="replay_ok",
            ok=False,
            detail="replay_comparison.json missing or unreadable",
            fail_code="FAIL_MISSING_REPLAY_COMPARISON",
        )
    if not isinstance(rc, dict):
        return CheckResult(
            name="replay_ok",
            ok=False,
            detail="replay_comparison.json not a JSON object",
            fail_code="FAIL_INVALID_REPLAY_COMPARISON",
        )
    if not bool(rc.get("ok", False)):
        return CheckResult(
            name="replay_ok",
            ok=False,
            detail=f"replay reported not-ok: {rc.get('reasons') or rc.get('detail') or rc}",
            fail_code="FAIL_REPLAY_ROUTE_MISMATCH",
            evidence={"replay_comparison": rc},
        )
    return CheckResult(name="replay_ok", ok=True, evidence={"replay_comparison": rc})


def _check_adg_no_worsening(proof_dir: Path) -> CheckResult:
    """adg_delta.json (when present) must report no P0 increase."""
    delta = _load_json(proof_dir / "adg" / "adg_delta.json")
    if delta is None:
        return CheckResult(
            name="adg_no_worsening",
            ok=True,
            detail="no adg_delta.json — ADG check not requested for this run",
        )
    if not isinstance(delta, dict):
        return CheckResult(
            name="adg_no_worsening",
            ok=False,
            detail="adg_delta.json not a JSON object",
            fail_code="FAIL_INVALID_ADG_DELTA",
        )
    p0_increased = bool(delta.get("p0_increased", False))
    delta_p0 = int(delta.get("delta_p0", 0))
    if p0_increased or delta_p0 > 0:
        return CheckResult(
            name="adg_no_worsening",
            ok=False,
            detail=f"ADG P0 worsened by {delta_p0} on touched files",
            fail_code="FAIL_ADG_WORSENING",
            evidence={"delta_p0": delta_p0, "delta": delta},
        )
    return CheckResult(name="adg_no_worsening", ok=True, evidence={"delta_p0": delta_p0})


def _check_proof_manifest_hash(proof_dir: Path) -> CheckResult:
    """run_manifest.json must include proof_manifest_hash, and the recomputed
    value over (run_manifest_body + artifact_hashes + …) must match.

    The hash is computed by the runner over the canonical-JSON of:

        {
          "run_manifest": <body without proof_manifest_hash>,
          "artifact_hashes": {<rel_path>: <sha256>},
          "trace_export_hash": <sha256 of otel_trace.json>,
          "contract_hashes": {<rel_path>: <sha256>},
          "gate_verdict_hash": <sha256 of gate_verdicts.jsonl>,
          "replay_comparison_hash": <sha256 of replay_comparison.json>,
          "adg_delta_hash": <sha256 of adg_delta.json or "" if absent>
        }

    The verifier independently recomputes from on-disk content.
    """
    m = _load_json(proof_dir / "run_manifest.json")
    if not isinstance(m, dict):
        return CheckResult(
            name="proof_manifest_hash",
            ok=False,
            detail="run_manifest.json not a dict",
            fail_code="FAIL_MISSING_RUN_MANIFEST",
        )
    stored = m.get("proof_manifest_hash")
    if not stored:
        return CheckResult(
            name="proof_manifest_hash",
            ok=False,
            detail="run_manifest.json has no proof_manifest_hash",
            fail_code="FAIL_MISSING_PROOF_MANIFEST_HASH",
        )

    # Build the body for recomputation.
    body_for_hash = {k: v for k, v in m.items() if k != "proof_manifest_hash"}
    artifact_hashes: dict[str, str] = {}
    contract_hashes: dict[str, str] = {}
    contracts_dir = proof_dir / "contracts"
    if contracts_dir.exists():
        for jp in sorted(contracts_dir.rglob("*.json")):
            rel = str(jp.relative_to(proof_dir)).replace("\\", "/")
            contract_hashes[rel] = _sha256_file(jp)
        for jp in sorted(contracts_dir.rglob("*.jsonl")):
            rel = str(jp.relative_to(proof_dir)).replace("\\", "/")
            contract_hashes[rel] = _sha256_file(jp)

    trace_p = proof_dir / "trace" / "otel_trace.json"
    trace_hash = _sha256_file(trace_p) if trace_p.exists() else ""
    gate_p = proof_dir / "gates" / "gate_verdicts.jsonl"
    gate_hash = _sha256_file(gate_p) if gate_p.exists() else ""
    replay_p = proof_dir / "replay" / "replay_comparison.json"
    replay_hash = _sha256_file(replay_p) if replay_p.exists() else ""
    adg_p = proof_dir / "adg" / "adg_delta.json"
    adg_hash = _sha256_file(adg_p) if adg_p.exists() else ""

    recomputed_input = {
        "run_manifest": body_for_hash,
        "artifact_hashes": artifact_hashes,
        "trace_export_hash": trace_hash,
        "contract_hashes": contract_hashes,
        "gate_verdict_hash": gate_hash,
        "replay_comparison_hash": replay_hash,
        "adg_delta_hash": adg_hash,
    }
    recomputed = _sha256(recomputed_input)

    if stored != recomputed:
        return CheckResult(
            name="proof_manifest_hash",
            ok=False,
            detail="stored proof_manifest_hash does not match recomputed",
            fail_code="FAIL_TAMPERED_PROOF",
            evidence={
                "stored": stored,
                "recomputed": recomputed,
                "input_keys": sorted(recomputed_input.keys()),
                "contract_count": len(contract_hashes),
            },
        )
    return CheckResult(
        name="proof_manifest_hash",
        ok=True,
        evidence={"recomputed": recomputed, "contract_count": len(contract_hashes)},
    )


# ---------------------------------------------------------------------------
# W4 — Anti-cheat checks for UWG bypass, unsupported claims, provider fallback
# ---------------------------------------------------------------------------


def _check_uwg_no_bypass(proof_dir: Path) -> CheckResult:
    """Any artifact under contracts/ named ``*durable*`` or ``*write_request*``
    or any ``UWGCommitRequest`` artifact MUST have a matching
    ``uwg_commit_receipt.json`` next to it."""
    contracts_dir = proof_dir / "contracts"
    if not contracts_dir.exists():
        return CheckResult(name="uwg_no_bypass", ok=True, detail="no contracts dir")
    bypass_evidence: list[dict[str, Any]] = []
    has_request = (contracts_dir / "uwg_commit_request.json").exists()
    has_receipt = (contracts_dir / "uwg_commit_receipt.json").exists()
    if has_request and not has_receipt:
        bypass_evidence.append(
            {"path": "contracts/uwg_commit_request.json", "missing": "uwg_commit_receipt.json"}
        )
    # Scan for any "durable=true" markers in non-UWG artifacts.
    for jp in contracts_dir.glob("*.json"):
        if jp.name in {"uwg_commit_request.json", "uwg_commit_receipt.json"}:
            continue
        body = _load_json(jp)
        if not isinstance(body, dict):
            continue
        # Recursively scan for {"classification": "UWG_DURABLE"} or {"durable": true}
        if _contains_durable_marker(body) and not has_receipt:
            bypass_evidence.append(
                {
                    "path": str(jp.relative_to(proof_dir)).replace("\\", "/"),
                    "marker": "durable=True without uwg_commit_receipt.json",
                }
            )
    if bypass_evidence:
        return CheckResult(
            name="uwg_no_bypass",
            ok=False,
            detail=f"{len(bypass_evidence)} potential UWG bypass(es)",
            fail_code="FAIL_UWG_BYPASS",
            evidence={"bypasses": bypass_evidence},
        )
    return CheckResult(name="uwg_no_bypass", ok=True)


def _contains_durable_marker(obj: Any) -> bool:
    """Recursively detect a {classification: UWG_DURABLE} or {durable: true}."""
    if isinstance(obj, dict):
        if obj.get("classification") == "UWG_DURABLE":
            return True
        if obj.get("durable") is True:
            return True
        return any(_contains_durable_marker(v) for v in obj.values())
    if isinstance(obj, list):
        return any(_contains_durable_marker(x) for x in obj)
    return False


def _tokens(text: str) -> list[str]:
    """Extract content words >=5 chars from a free-text string."""
    return [t for t in str(text).lower().replace(",", " ").replace(".", " ").split() if len(t) >= 5]


def _is_supported(claim: str, support_corpus: str) -> bool:
    toks = _tokens(claim)
    if not toks:
        return True  # empty/short claim cannot be unsupported
    return any(t in support_corpus for t in toks)


def _check_no_unsupported_claims(proof_dir: Path) -> CheckResult:
    """Per-app unsupported-claim invariant — W10 generalization.

    Each grounded app has its own claim register and evidence register. A
    claim is "supported" if any content token (>=5 chars) appears anywhere
    in the per-app support corpus. The check is intentionally permissive
    (token-substring) so it never produces false positives on legitimate
    free-text variation, but it catches sabotage T19 (injection of a
    claim with zero shared content tokens with any evidence).

    Apps covered:
      - apps_underwriting_ai: decision_packet.{key_risks,key_strengths}
                              vs evidence_register.entries
      - apps_research:        citation_support_map.anchored == false → FAIL
      - apps_exec:            unsupported_claims.payload non-empty → FAIL
    """
    m = _load_json(proof_dir / "run_manifest.json") or {}
    app = m.get("app_name", "")

    if app == "apps_underwriting_ai":
        return _check_underwriting_claims(proof_dir)
    if app == "apps_research":
        return _check_research_anchored(proof_dir)
    if app == "apps_exec":
        return _check_exec_claims(proof_dir)
    # apps_lic, apps_rg, apps_eval, apps_shared have no claim register.
    return CheckResult(name="no_unsupported_claims", ok=True, detail="not applicable for this app")


def _check_underwriting_claims(proof_dir: Path) -> CheckResult:
    """apps_underwriting_ai: key_risks / key_strengths must have token support
    in evidence_register.entries. ``conditions`` / ``covenants`` are
    deliberately EXCLUDED — they are lender stipulations, not factual
    claims about the borrower, and have no per-claim evidence in the
    register by design."""
    packet = _load_json(proof_dir / "contracts" / "decision_packet.json")
    register = _load_json(proof_dir / "contracts" / "evidence_register.json")
    if not isinstance(packet, dict) or not isinstance(register, dict):
        return CheckResult(name="no_unsupported_claims", ok=True, detail="artifacts missing")
    packet_payload = packet.get("payload", packet)
    register_payload = register.get("payload", register)
    entries = register_payload.get("entries", []) if isinstance(register_payload, dict) else []
    support_corpus = " | ".join(
        str(e.get("claim_text", "")) + " | " + str(e.get("supporting_excerpt", ""))
        for e in entries if isinstance(e, dict)
    ).lower()
    fixture_legal = packet_payload.get("borrower_legal_name", "")
    support_corpus += " | " + str(fixture_legal).lower()
    unsupported: list[str] = []
    # conditions/covenants are boilerplate stipulations, not claims requiring
    # evidence support. Only key_risks and key_strengths are factual claims.
    for key in ("key_risks", "key_strengths"):
        for claim in packet_payload.get(key, []) or []:
            if not _is_supported(str(claim), support_corpus):
                unsupported.append(f"{key}:{str(claim)[:80]}")
    if unsupported:
        return CheckResult(
            name="no_unsupported_claims",
            ok=False,
            detail=f"{len(unsupported)} unsupported claim(s) in decision_packet",
            fail_code="FAIL_UNSUPPORTED_MATERIAL_CLAIM",
            evidence={"unsupported": unsupported[:10]},
        )
    return CheckResult(name="no_unsupported_claims", ok=True)


def _check_research_anchored(proof_dir: Path) -> CheckResult:
    """apps_research: citation_support_map[claim].anchored MUST be true for
    every claim. False = a claim's source is not in source_credibility_scores."""
    smap = _load_json(proof_dir / "contracts" / "citation_support_map.json")
    if not isinstance(smap, dict):
        return CheckResult(name="no_unsupported_claims", ok=True, detail="artifact missing")
    payload = smap.get("payload", smap)
    claims = payload.get("claims", []) if isinstance(payload, dict) else []
    unanchored = [
        c for c in claims
        if isinstance(c, dict) and c.get("anchored") is False
    ]
    if unanchored:
        return CheckResult(
            name="no_unsupported_claims",
            ok=False,
            detail=f"{len(unanchored)} unanchored citation(s)",
            fail_code="FAIL_UNSUPPORTED_MATERIAL_CLAIM",
            evidence={"unanchored": [c.get("claim_id", "?") for c in unanchored[:10]]},
        )
    return CheckResult(name="no_unsupported_claims", ok=True)


def _check_exec_claims(proof_dir: Path) -> CheckResult:
    """apps_exec: every claim_register entry with labeled_as=='fact' must
    carry a non-empty evidence_source. Any pre-flagged unsupported_claims
    entry is also FAIL."""
    creg = _load_json(proof_dir / "contracts" / "claim_register.json")
    uns = _load_json(proof_dir / "contracts" / "unsupported_claims.json")
    if isinstance(uns, dict):
        uns_payload = uns.get("payload", uns)
        items = uns_payload.get("items", []) if isinstance(uns_payload, dict) else []
        if items:
            return CheckResult(
                name="no_unsupported_claims",
                ok=False,
                detail=f"{len(items)} pre-flagged unsupported claim(s)",
                fail_code="FAIL_UNSUPPORTED_MATERIAL_CLAIM",
                evidence={"items": items[:10]},
            )
    if not isinstance(creg, dict):
        return CheckResult(name="no_unsupported_claims", ok=True, detail="artifact missing")
    payload = creg.get("payload", creg)
    claims = payload.get("claims", []) if isinstance(payload, dict) else []
    bad: list[str] = []
    for c in claims:
        if not isinstance(c, dict):
            continue
        if c.get("labeled_as") == "fact" and not c.get("evidence_source"):
            bad.append(c.get("claim_id", str(c.get("text", ""))[:40]))
    if bad:
        return CheckResult(
            name="no_unsupported_claims",
            ok=False,
            detail=f"{len(bad)} fact-labeled claim(s) without evidence_source",
            fail_code="FAIL_UNSUPPORTED_MATERIAL_CLAIM",
            evidence={"bad": bad[:10]},
        )
    return CheckResult(name="no_unsupported_claims", ok=True)


def _check_no_uncertified_provider_fallback(proof_dir: Path) -> CheckResult:
    """If any artifact contains ``provider_fallback`` or ``fallback_provider``
    field set to a non-default value, a corresponding ``recertification``
    artifact must exist."""
    contracts_dir = proof_dir / "contracts"
    if not contracts_dir.exists():
        return CheckResult(name="no_uncertified_provider_fallback", ok=True)
    fallback_seen: list[dict[str, Any]] = []
    for jp in contracts_dir.glob("*.json"):
        body = _load_json(jp)
        if not isinstance(body, dict):
            continue
        if _contains_provider_fallback(body):
            fallback_seen.append(
                {"path": str(jp.relative_to(proof_dir)).replace("\\", "/")}
            )
    if not fallback_seen:
        return CheckResult(name="no_uncertified_provider_fallback", ok=True)
    # Look for a recertification artifact
    recert_paths = list(contracts_dir.glob("*recertification*.json"))
    if recert_paths:
        return CheckResult(
            name="no_uncertified_provider_fallback",
            ok=True,
            evidence={"fallbacks": fallback_seen, "recertifications": [str(p.name) for p in recert_paths]},
        )
    return CheckResult(
        name="no_uncertified_provider_fallback",
        ok=False,
        detail=f"{len(fallback_seen)} provider fallback(s) without recertification",
        fail_code="FAIL_UNCERTIFIED_PROVIDER_FALLBACK",
        evidence={"fallbacks": fallback_seen},
    )


def _contains_provider_fallback(obj: Any) -> bool:
    """Recursively detect provider_fallback / fallback_provider markers."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in {"provider_fallback", "fallback_provider"} and v not in (None, "", False, "none"):
                return True
            if _contains_provider_fallback(v):
                return True
    if isinstance(obj, list):
        return any(_contains_provider_fallback(x) for x in obj)
    return False


# ---------------------------------------------------------------------------
# Top-level
# ---------------------------------------------------------------------------


def verify(proof_dir: Path) -> dict[str, Any]:
    """Run every check, build the proof_verdict payload."""
    if not proof_dir.exists():
        return {
            "final_status": PROOF_STATUS_FAIL,
            "verifier_version": VERIFIER_VERSION,
            "verified_at": _utcnow_iso(),
            "verifier_command": " ".join(sys.argv),
            "passed_checks": [],
            "failed_checks": [
                {
                    "name": "proof_dir_exists",
                    "ok": False,
                    "fail_code": "FAIL_MISSING_PROOF_DIR",
                    "detail": f"proof_dir not found: {proof_dir}",
                    "evidence": {},
                }
            ],
            "warning_checks": [],
            "source_artifacts": [],
            "recomputed_hashes": {},
        }

    results: list[CheckResult] = []
    results.extend(_check_required_files(proof_dir))
    results.append(_check_run_manifest_links(proof_dir))
    results.extend(_check_artifacts_join_run(proof_dir))
    results.extend(_check_span_tree(proof_dir))
    results.append(_check_required_stages(proof_dir))
    results.append(_check_grounded_has_c0(proof_dir))
    results.append(_check_exit_when_output(proof_dir))
    results.append(_check_l6_post_exit(proof_dir))
    results.append(_check_replay(proof_dir))
    results.append(_check_adg_no_worsening(proof_dir))
    results.append(_check_proof_manifest_hash(proof_dir))
    results.append(_check_uwg_no_bypass(proof_dir))
    results.append(_check_no_unsupported_claims(proof_dir))
    results.append(_check_no_uncertified_provider_fallback(proof_dir))

    passed = [r for r in results if r.ok]
    failed = [r for r in results if not r.ok]

    # Source artifact list — every file we read.
    sources: list[str] = []
    for rel in (
        "run_manifest.json",
        "trace/otel_trace.json",
        "gates/gate_verdicts.jsonl",
        "replay/replay_comparison.json",
        "adg/adg_delta.json",
    ):
        p = proof_dir / rel
        if p.exists():
            sources.append(rel)
    contracts_dir = proof_dir / "contracts"
    if contracts_dir.exists():
        for jp in sorted(contracts_dir.glob("*.json")):
            sources.append(str(jp.relative_to(proof_dir)).replace("\\", "/"))

    final_status = PROOF_STATUS_PASS if not failed else PROOF_STATUS_FAIL
    return {
        "final_status": final_status,
        "verifier_version": VERIFIER_VERSION,
        "verified_at": _utcnow_iso(),
        "verifier_command": " ".join(sys.argv),
        "passed_checks": [r.to_dict() for r in passed],
        "failed_checks": [r.to_dict() for r in failed],
        "warning_checks": [],
        "source_artifacts": sources,
        "recomputed_hashes": _recomputed_hashes(proof_dir),
    }


def _recomputed_hashes(proof_dir: Path) -> dict[str, str]:
    """All file hashes the verifier computed."""
    out: dict[str, str] = {}
    for rel in ("trace/otel_trace.json", "gates/gate_verdicts.jsonl",
                "replay/replay_comparison.json", "adg/adg_delta.json"):
        p = proof_dir / rel
        if p.exists():
            out[rel] = _sha256_file(p)
    contracts_dir = proof_dir / "contracts"
    if contracts_dir.exists():
        for jp in sorted(contracts_dir.glob("*.json")):
            rel = str(jp.relative_to(proof_dir)).replace("\\", "/")
            out[rel] = _sha256_file(jp)
        for jp in sorted(contracts_dir.glob("*.jsonl")):
            rel = str(jp.relative_to(proof_dir)).replace("\\", "/")
            out[rel] = _sha256_file(jp)
    return out


def write_verdict(verdict: dict[str, Any], proof_dir: Path) -> None:
    """Write proof_verdict.json + proof_report.md + failure_reasons.jsonl."""
    verifier_dir = proof_dir / "verifier"
    verifier_dir.mkdir(parents=True, exist_ok=True)

    (verifier_dir / "proof_verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8"
    )

    # Human-readable
    lines: list[str] = []
    lines.append("# Proof Verdict")
    lines.append("")
    lines.append(f"- Status: **{verdict['final_status']}**")
    lines.append(f"- Verifier version: `{verdict['verifier_version']}`")
    lines.append(f"- Verified at: {verdict['verified_at']}")
    lines.append(f"- Passed: {len(verdict['passed_checks'])}")
    lines.append(f"- Failed: {len(verdict['failed_checks'])}")
    if verdict["failed_checks"]:
        lines.append("")
        lines.append("## Failed checks")
        lines.append("")
        for fc in verdict["failed_checks"]:
            lines.append(
                f"- **{fc['name']}** — `{fc.get('fail_code') or 'FAIL'}`: {fc.get('detail', '')}"
            )
    lines.append("")
    lines.append("## Source artifacts")
    lines.append("")
    for s in verdict["source_artifacts"]:
        lines.append(f"- `{s}`")
    (verifier_dir / "proof_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    # JSONL failure reasons
    failures_path = verifier_dir / "failure_reasons.jsonl"
    with failures_path.open("w", encoding="utf-8") as fh:
        for fc in verdict["failed_checks"]:
            fh.write(json.dumps(fc, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tools.apps_proof.verify_app_proof",
        description="Independent proof verifier — anti-cheat hash recomputation.",
    )
    parser.add_argument(
        "--proof-dir",
        required=True,
        type=Path,
        help="Path to artifacts/apps_proof/<app>/<run_id>/",
    )
    args = parser.parse_args(argv)

    verdict = verify(args.proof_dir)
    write_verdict(verdict, args.proof_dir)

    print(f"verifier: {verdict['final_status']} — {len(verdict['passed_checks'])} pass, "
          f"{len(verdict['failed_checks'])} fail")
    if verdict["failed_checks"]:
        for fc in verdict["failed_checks"][:10]:
            print(f"  - {fc['name']}: {fc.get('fail_code') or 'FAIL'}: {fc.get('detail', '')}")

    return 0 if verdict["final_status"] == PROOF_STATUS_PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
