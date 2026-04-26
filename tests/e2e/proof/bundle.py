"""Proof bundle schema and IO helpers (per 99.8).

A proof bundle is the durable artifact emitted by the E2E harness for one or
more scenarios. Validators consume bundles to render PASS / FAIL / PARTIAL.
"""

from __future__ import annotations

import dataclasses as _dc
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tqdm import tqdm

from .contracts import ProofStatus
from .digests import digest


# ---------------------------------------------------------------------------
# Per-scenario bundle entry
# ---------------------------------------------------------------------------


@dataclass
class ScenarioOutcome:
    scenario_id: str
    scenario_status: ProofStatus
    expected_path: list[str]
    observed_path: list[str]
    contracts: dict[str, Any] = field(default_factory=dict)
    traces: list[dict[str, Any]] = field(default_factory=list)
    replay_receipts: list[dict[str, Any]] = field(default_factory=list)
    no_bypass_receipts: list[dict[str, Any]] = field(default_factory=list)
    groundedness_receipts: list[dict[str, Any]] = field(default_factory=list)
    disposition_receipts: list[dict[str, Any]] = field(default_factory=list)
    uwg_receipts: list[dict[str, Any]] = field(default_factory=list)
    l6_exhaust_receipts: list[dict[str, Any]] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Top-level bundle
# ---------------------------------------------------------------------------


@dataclass
class E2EProofBundle:
    bundle_id: str
    generated_at: str
    repo_commit: str
    scenario_set: str
    policy_hash: str
    blueprint_hash: str
    registry_digest: str
    tests_run: int
    scenarios: list[ScenarioOutcome] = field(default_factory=list)
    failure_summary: list[str] = field(default_factory=list)
    acceptance_status: ProofStatus = ProofStatus.PARTIAL


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------


def _to_jsonable(obj: Any) -> Any:
    """Recursively convert dataclasses + enums to JSON-friendly types."""
    if hasattr(obj, "value") and isinstance(obj, ProofStatus):
        return obj.value
    if _dc.is_dataclass(obj) and not isinstance(obj, type):
        return {k: _to_jsonable(v) for k, v in _dc.asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    if hasattr(obj, "value") and obj.__class__.__bases__ and obj.__class__.__bases__[0] is not object:
        # generic Enum fallback
        try:
            return obj.value  # type: ignore[attr-defined]
        except AttributeError:
            return repr(obj)
    return obj


def write_bundle(bundle: E2EProofBundle, dest_dir: Path) -> Path:
    """Write the bundle to ``<dest_dir>/bundle.json`` and return its path.

    Also writes individual scenario contract artifacts under
    ``<dest_dir>/scenarios/<scenario_id>/`` so 99.1's required-artifact
    list (gp_001_route_contract.json, etc.) is satisfied verbatim.
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    payload = _to_jsonable(bundle)
    payload["digest"] = digest(payload)
    bundle_path = dest_dir / "bundle.json"
    bundle_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    scenarios_root = dest_dir / "scenarios"
    scenarios_root.mkdir(parents=True, exist_ok=True)
    iter_scenarios = tqdm(
        bundle.scenarios,
        desc="Writing scenario artifacts",
        unit="scenario",
        disable=len(bundle.scenarios) < 5,
    )
    for scenario in iter_scenarios:
        s_dir = scenarios_root / scenario.scenario_id
        s_dir.mkdir(parents=True, exist_ok=True)
        for name, contract_payload in scenario.contracts.items():
            artifact_name = _artifact_filename(scenario.scenario_id, name)
            (s_dir / artifact_name).write_text(
                json.dumps(_to_jsonable(contract_payload), indent=2, sort_keys=True),
                encoding="utf-8",
            )
        if scenario.traces:
            (s_dir / _artifact_filename(scenario.scenario_id, "otel_trace")).write_text(
                json.dumps(_to_jsonable(scenario.traces), indent=2, sort_keys=True),
                encoding="utf-8",
            )
        receipt_groups = {
            "replay_receipt": scenario.replay_receipts,
            "no_bypass_receipt": scenario.no_bypass_receipts,
            "groundedness_receipt": scenario.groundedness_receipts,
            "disposition": scenario.disposition_receipts,
            "uwg_receipt": scenario.uwg_receipts,
            "l6_exhaust_receipt": scenario.l6_exhaust_receipts,
        }
        for kind, receipts in tqdm(
            receipt_groups.items(),
            desc=f"  receipts/{scenario.scenario_id}",
            unit="kind",
            leave=False,
            disable=True,
        ):
            if receipts:
                (s_dir / _artifact_filename(scenario.scenario_id, kind)).write_text(
                    json.dumps(_to_jsonable(receipts), indent=2, sort_keys=True),
                    encoding="utf-8",
                )

    return bundle_path


def read_bundle(src_dir: Path) -> dict[str, Any]:
    """Read bundle JSON back as a plain dict (no re-hydration of dataclasses)."""
    src_dir = Path(src_dir)
    bundle_path = src_dir / "bundle.json"
    data: dict[str, Any] = json.loads(bundle_path.read_text(encoding="utf-8"))
    return data


def verify_bundle_integrity(src_dir: Path) -> tuple[bool, str]:
    """Re-compute the bundle digest from disk and compare to the declared field.

    Returns ``(ok, reason)`` — used by tests and CI to detect on-disk tamper of
    a previously-emitted proof bundle.
    """
    data = read_bundle(src_dir)
    declared = data.pop("digest", None)
    if not declared:
        return (False, "bundle.json has no declared digest field")
    recomputed = digest(data)
    if declared != recomputed:
        return (False, f"declared {declared!r} != recomputed {recomputed!r}")
    return (True, "ok")


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


_CONTRACT_FILENAME_MAP = {
    "ValidatedRequest": "request",
    "L1PlanContract": "l1_plan",
    "RouteContract": "route_contract",
    "FinalEvidenceContract": "final_evidence_contract",
    "PromptEnvelope": "prompt_envelope",
    "L2ExecutionRequest": "l2_execution_request",
    "L3WorkflowContract": "l3_workflow_contract",
    "SealedL2Artifact": "sealed_l2_artifact",
    "ExitReviewPacket": "exit_review_packet",
    "X3DispositionReceipt": "x3_disposition",
    "CommitRequest": "commit_request",
    "UWGCommitReceipt": "uwg_commit_receipt",
    "RuntimeExhaustBundle": "runtime_exhaust_bundle",
}


def _artifact_filename(scenario_id: str, kind: str) -> str:
    """Produce a 99.1-compliant artifact filename like ``gp_001_route_contract.json``.

    Contract dataclass names (e.g. ``RouteContract``) are normalized to the
    snake-case form 99.1 spells out verbatim. Receipt names (e.g.
    ``replay_receipt``) pass through unchanged.
    """
    safe_id = scenario_id.lower().replace("-", "_")
    snake = _CONTRACT_FILENAME_MAP.get(kind, kind)
    return f"{safe_id}_{snake}.json"


def repo_commit() -> str:
    """Best-effort repo commit. Reads a HEAD env override first, then ``git``."""
    override = os.environ.get("E2E_REPO_COMMIT")
    if override:
        return override
    head = Path.cwd() / ".git" / "HEAD"
    try:
        if head.exists():
            ref_line = head.read_text(encoding="utf-8").strip()
            if ref_line.startswith("ref:"):
                ref_path = Path.cwd() / ".git" / ref_line.split(" ", 1)[1].strip()
                if ref_path.exists():
                    return ref_path.read_text(encoding="utf-8").strip()
            return ref_line
    except OSError:
        pass
    return "unknown"


__all__ = [
    "ScenarioOutcome",
    "E2EProofBundle",
    "write_bundle",
    "read_bundle",
    "now_iso",
    "repo_commit",
    "_artifact_filename",
]
