"""W3 validators — trace tree + replay determinism + artifact inventory.

These validators enforce the §10 acceptance criteria from the prompt:

* :func:`validate_trace_tree` — every trace must have a single root span,
  every parent_span_id must reference an emitted span, and the layer order
  must respect the canonical spine sequence (U0 → L1 → L0 → L3 → Exit → ...).

* :func:`validate_replay` — running a scenario twice with the same seed must
  produce byte-identical content for ValidatedRequest, L1PlanContract, and
  RouteContract. Timestamps are excluded from comparison since wall-clock
  differs even with deterministic IDs.

* :func:`validate_artifact_inventory` — every path referenced in the
  evidence packet's contract_inventory / span_inventory / gate_verdict_inventory
  / artifact_inventory must exist on disk and be non-empty.

A scenario is W3-PASS only when all three validators return :class:`Verdict`
with ``ok=True``.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps_shared.proof.proof_contracts import (
    AppRunEvidencePacket,
    sha256_of,
    sha256_of_file,
    verify_packet_hash,
)
from apps_shared.proof.scenario_base import ScenarioSpec, run_app_scenario
from apps_shared.proof.scenarios import RegisteredScenario


# ---------------------------------------------------------------------------
# Verdict dataclass
# ---------------------------------------------------------------------------


@dataclass
class Verdict:
    """Generic validator outcome — ok=False means W3 FAIL."""

    name: str
    ok: bool
    fail_reasons: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "ok": self.ok,
            "fail_reasons": list(self.fail_reasons),
            "details": dict(self.details),
        }


# ---------------------------------------------------------------------------
# 1. Trace tree validator
# ---------------------------------------------------------------------------


# Canonical spine layer order. A span at position N can have a parent span
# at any earlier position. Spans of the same layer are allowed (e.g. L5
# customizer assertion + L6 firewall assertion). Layers absent from the
# trace are ignored — only the relative order of present layers matters.
_CANONICAL_LAYER_ORDER = (
    "U0",
    "L1",
    "L0",
    "C0",
    "PromptAssembly",
    "L3",
    "L2",
    "Exit",
    "UWG",
    "L5",
    "L6",
    "customizer",
)


def validate_trace_tree(trace_path: Path | str) -> Verdict:
    """Verify the span tree is well-formed.

    Required invariants:
      1. Trace JSON is a non-empty list of span records
      2. Exactly one root (span with parent_span_id=None)
      3. Every parent_span_id references an emitted span_id
      4. trace_id is consistent across all spans
      5. Layer order respects the canonical spine sequence
    """
    p = Path(trace_path)
    if not p.exists():
        return Verdict("trace_tree", False, [f"missing: {p}"])
    try:
        spans = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return Verdict("trace_tree", False, [f"invalid json: {exc}"])
    if not isinstance(spans, list) or not spans:
        return Verdict("trace_tree", False, ["spans is empty or not a list"])

    fail: list[str] = []
    roots = [s for s in spans if s.get("parent_span_id") is None]
    if len(roots) != 1:
        fail.append(f"expected exactly 1 root, found {len(roots)}")

    span_ids = {s.get("span_id") for s in spans}
    for s in spans:
        pid = s.get("parent_span_id")
        if pid is not None and pid not in span_ids:
            fail.append(f"span {s.get('span_id')} references missing parent {pid}")

    trace_ids = {s.get("trace_id") for s in spans}
    # BUG-FIX (2026-04-26): if every span has trace_id=None, the set is {None}
    # with len=1, which previously passed this check. A trace with no
    # trace_id is structurally invalid — fail explicitly.
    if None in trace_ids:
        fail.append(f"span(s) missing trace_id (None present): {sorted(s.get('span_id', '?') for s in spans if s.get('trace_id') is None)[:5]}")
    if len(trace_ids - {None}) > 1:
        fail.append(f"inconsistent trace_id values: {sorted(t for t in trace_ids if t is not None)}")
    elif len(trace_ids) > 1 and None in trace_ids:
        # mixed: some spans have trace_id, some have None
        fail.append("trace_id mixed: some spans missing, others present")

    # Layer order check
    canonical_index = {layer: i for i, layer in enumerate(_CANONICAL_LAYER_ORDER)}
    last_idx = -1
    for s in spans:
        layer = s.get("layer")
        if layer not in canonical_index:
            # Unknown layer — record but don't fail (extensibility)
            continue
        idx = canonical_index[layer]
        if idx < last_idx:
            fail.append(f"layer {layer} (idx {idx}) appears after later layer (idx {last_idx})")
        last_idx = max(last_idx, idx)

    return Verdict(
        name="trace_tree",
        ok=not fail,
        fail_reasons=fail,
        details={
            "span_count": len(spans),
            "root_count": len(roots),
            "trace_id": next(iter(trace_ids), None),
            "layers_present": sorted({s.get("layer") for s in spans}),
        },
    )


# ---------------------------------------------------------------------------
# 2. Replay determinism validator
# ---------------------------------------------------------------------------


def _read_contract_payload(scenario_dir: Path, contract_kind: str) -> dict[str, Any] | None:
    """Find the latest contract of the given kind in scenario_dir.

    BUG-FIX (2026-04-26 audit pass 2 / #11): if a contract file exists but
    contains malformed JSON (e.g. truncated by a tamper, partial write
    interrupted by a crash), ``json.loads`` raises ``JSONDecodeError`` and
    propagates up out of ``validate_replay``. Caller-side try/except in
    proof_runner doesn't catch it. Defensive: return None on parse error
    so the replay validator surfaces a clean "missing in primary or replay"
    fail reason instead of crashing the whole run.
    """
    matches = sorted(scenario_dir.glob(f"{contract_kind}_*.json"))
    if not matches:
        return None
    try:
        parsed = json.loads(matches[-1].read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):  # guardian: allow-return-none-swallow -- replay contract loader returns None on malformed/missing JSON; caller surfaces missing-contract fail reason
        return None
    # BUG-FIX (audit pass 3 / BUG #13, found by Hypothesis): json.loads
    # can legitimately return a list / string / number / null when the file
    # is valid JSON but the wrong shape. Returning a non-dict here later
    # crashes _strip_volatile / sha256_of with TypeError. Treat any non-dict
    # result as a missing contract — caller handles None gracefully.
    if not isinstance(parsed, dict):
        return None
    return parsed


def _strip_volatile(payload: Any) -> Any:
    """Drop fields that legitimately differ run-to-run.

    These fall into three categories:

    1. Wall-clock timestamps: caller-side clock samples that the proof
       harness cannot pin without monkey-patching the system clock. Any
       field name ending in ``_at_iso``, ``_at_observed``, ``_at_utc``, or
       ``_time_unix`` is a wall-clock sample.

    2. Internally-generated UUIDs: IntakePipeline issues fresh UUIDs for
       every receipt (transport, identity, quota, schema, correlation,
       replay seed). These are run-instance metadata; their values change
       per-invocation by design. Any field name ending in ``_receipt_ref``
       or ``_seed_ref`` is run-instance metadata.

    3. A small explicit allowlist of legacy field names that don't match
       the suffix patterns but are still volatile.
    """
    if isinstance(payload, dict):
        out: dict[str, Any] = {}
        for k, v in payload.items():
            # Suffix-based: any wall-clock sample or run-instance UUID receipt
            if k.endswith(
                (
                    "_at_iso",
                    "_at_observed",
                    "_at_utc",
                    "_time_unix",
                    "_receipt_ref",
                    "_seed_ref",
                )
            ):
                continue
            # Explicit allowlist for fields that don't fit the suffix pattern
            if k in {
                "created_at",
                "started_at",
                "ended_at",
                "timestamp",
                "wall_clock_utc",
            }:
                continue
            out[k] = _strip_volatile(v)
        return out
    if isinstance(payload, list):
        return [_strip_volatile(x) for x in payload]
    return payload


def validate_replay(
    *,
    registered: RegisteredScenario,
    export_root: Path,
    adg_snapshot: Path,
) -> Verdict:
    """Re-run the scenario in a sibling directory with the same seed and
    compare contract content (timestamps stripped).

    Output: ``replay/<app_id>/<scenario_id>/`` mirrors the structure of the
    primary export but the second run's content. The validator hashes the
    timestamp-stripped contracts from both runs and reports the diff.
    """
    spec = registered.spec
    replay_root = export_root / "replay" / spec.app_id

    # Clean any previous replay dir for this scenario so we get a fresh run
    if replay_root.exists():
        shutil.rmtree(replay_root, ignore_errors=True)
    replay_root.mkdir(parents=True, exist_ok=True)

    try:
        replay_packet = run_app_scenario(
            spec,
            export_root=replay_root,
            adg_snapshot=adg_snapshot,
            customizer=registered.customizer,
            seed=spec.scenario_id,  # explicit — same as default
        )
    except (RuntimeError, ValueError, TypeError, AttributeError, ImportError) as exc:
        return Verdict("replay", False, [f"replay run raised: {exc!r}"])

    # Compare ID stability — these MUST match across runs
    primary_packet_path = export_root / "contracts" / spec.app_id / spec.scenario_id / "evidence_packet.json"
    if not primary_packet_path.exists():
        return Verdict("replay", False, [f"primary packet missing: {primary_packet_path}"])
    primary = json.loads(primary_packet_path.read_text(encoding="utf-8"))

    fail: list[str] = []
    id_compare = {}
    for field_name in ("run_id", "session_id", "request_id", "trace_root", "trace_id"):
        a = primary.get(field_name)
        b = getattr(replay_packet, field_name, None)
        id_compare[field_name] = {"primary": a, "replay": b, "match": a == b}
        if a != b:
            fail.append(f"id drift: {field_name} primary={a} replay={b}")

    # Compare each contract kind by content hash (timestamps stripped)
    primary_dir = export_root / "contracts" / spec.app_id / spec.scenario_id
    replay_dir = replay_root / "contracts" / spec.app_id / spec.scenario_id
    contract_compare = {}
    for kind in ("ValidatedRequest", "L1PlanContract", "RouteContract"):
        a_payload = _read_contract_payload(primary_dir, kind)
        b_payload = _read_contract_payload(replay_dir, kind)
        if a_payload is None or b_payload is None:
            contract_compare[kind] = {
                "primary_present": a_payload is not None,
                "replay_present": b_payload is not None,
                "match": False,
            }
            fail.append(f"{kind}: missing in primary or replay")
            continue
        a_hash = sha256_of(_strip_volatile(a_payload))
        b_hash = sha256_of(_strip_volatile(b_payload))
        contract_compare[kind] = {
            "primary_hash": a_hash,
            "replay_hash": b_hash,
            "match": a_hash == b_hash,
        }
        if a_hash != b_hash:
            fail.append(f"{kind}: content hash drift {a_hash[:8]} vs {b_hash[:8]}")

    return Verdict(
        name="replay",
        ok=not fail,
        fail_reasons=fail,
        details={
            "id_compare": id_compare,
            "contract_compare": contract_compare,
            "replay_packet_hash": replay_packet.packet_hash,
            "primary_packet_hash": primary.get("packet_hash"),
        },
    )


# ---------------------------------------------------------------------------
# 3. Artifact inventory validator
# ---------------------------------------------------------------------------


def validate_artifact_inventory(
    *,
    packet: AppRunEvidencePacket,
    export_root: Path,
    packet_path: Path | None = None,
) -> Verdict:
    """Every path in the inventories must exist on disk and be non-empty.

    Also re-verifies the packet hash on disk binds the JSON content (anti-tamper).

    BUG-FIX (2026-04-26): the packet's ``app_id`` / ``scenario_id`` fields
    are TAMPER-MUTABLE and must NOT be used to derive the on-disk packet
    path. Doing so let T2 (mutate-app_id-without-rehash) escape the actual
    hash check — the validator caught the tamper only because the derived
    path didn't exist. A move-and-tamper attack would have slipped past.

    Callers MUST pass an explicit ``packet_path`` derived from a trusted
    source (e.g. the registered scenario_id from disk discovery, not the
    loaded packet object). When ``packet_path`` is None the validator falls
    back to the legacy derivation but emits a ``trusted_path_unset`` reason
    code so the caller knows it's running in degraded mode.
    """
    fail: list[str] = []
    checked: list[dict[str, Any]] = []

    inventories = {
        "span": packet.span_inventory,
        "contract": packet.contract_inventory,
        "gate": packet.gate_verdict_inventory,
        "artifact": packet.artifact_inventory,
    }
    for kind, paths in inventories.items():
        for rel in paths:
            fp = export_root / rel
            entry: dict[str, Any] = {"kind": kind, "path": rel}
            if not fp.exists():
                entry["ok"] = False
                entry["reason"] = "missing"
                fail.append(f"{kind} inventory missing: {rel}")
            elif fp.stat().st_size == 0:
                entry["ok"] = False
                entry["reason"] = "empty"
                fail.append(f"{kind} inventory empty: {rel}")
            else:
                entry["ok"] = True
                entry["size_bytes"] = fp.stat().st_size
                entry["sha256"] = sha256_of_file(fp)
            checked.append(entry)

    # BUG-FIX (2026-04-26 audit pass 2 / #6): the inventory loop above only
    # checks that the INDEX files (artifact_inventory.json, gates JSON,
    # spans JSON) exist and are non-empty. The individual artifact files
    # they reference (sandbox/<app>/<id>.json, uwg_pending/<app>/<id>.json)
    # were NOT validated. An attacker could mutate
    # sandbox/apps_underwriting_ai/recommendation_v1.json (changing
    # "approve" → "reject") with no detection. Fix: walk INTO the
    # artifact_inventory.json, recompute sha256 of every referenced file,
    # compare against the recorded content_hash.
    for rel in packet.artifact_inventory:
        fp = export_root / rel
        if not fp.exists() or fp.stat().st_size == 0:
            continue  # already flagged in the loop above
        try:
            records = json.loads(fp.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail.append(f"artifact_inventory parse error in {rel}: {exc}")
            continue
        if not isinstance(records, list):
            fail.append(f"artifact_inventory in {rel} is not a list")
            continue
        for record in records:
            if not isinstance(record, dict):
                continue
            artifact_path = record.get("path")
            recorded_hash = record.get("content_hash")
            if not artifact_path or not recorded_hash:
                continue
            artifact_fp = export_root / artifact_path
            if not artifact_fp.exists():
                fail.append(
                    f"artifact file missing: {artifact_path} "
                    f"(referenced from {rel})"
                )
                continue
            actual_hash = sha256_of_file(artifact_fp)
            if actual_hash != recorded_hash:
                fail.append(
                    f"artifact content_hash drift: {artifact_path} "
                    f"recorded={recorded_hash[:8]} actual={actual_hash[:8]}"
                )

    # Re-verify packet hash as a separate check.
    # BUG-FIX: prefer the trusted packet_path provided by the caller. Only
    # fall back to deriving from packet fields if no trusted path is given.
    if packet_path is None:
        packet_path = (
            export_root / "contracts" / packet.app_id / packet.scenario_id
            / "evidence_packet.json"
        )
        fail_path_source = "trusted_path_unset"
    else:
        fail_path_source = "trusted"
    hash_ok, hash_msg = verify_packet_hash(packet_path)
    if not hash_ok:
        fail.append(f"packet_hash check failed: {hash_msg} (path_source={fail_path_source})")

    return Verdict(
        name="artifact_inventory",
        ok=not fail,
        fail_reasons=fail,
        details={
            "checked_count": len(checked),
            "checked": checked,
            "packet_hash_ok": hash_ok,
            "packet_hash_msg": hash_msg,
        },
    )


# ---------------------------------------------------------------------------
# Top-level: run all 3 validators for a scenario
# ---------------------------------------------------------------------------


@dataclass
class ScenarioValidationResult:
    """Combined W3 result for a single scenario."""

    app_id: str
    scenario_id: str
    trace_verdict: Verdict
    replay_verdict: Verdict
    inventory_verdict: Verdict

    @property
    def ok(self) -> bool:
        return self.trace_verdict.ok and self.replay_verdict.ok and self.inventory_verdict.ok

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_id": self.app_id,
            "scenario_id": self.scenario_id,
            "ok": self.ok,
            "trace_verdict": self.trace_verdict.to_dict(),
            "replay_verdict": self.replay_verdict.to_dict(),
            "inventory_verdict": self.inventory_verdict.to_dict(),
        }


def validate_scenario(
    *,
    registered: RegisteredScenario,
    packet: AppRunEvidencePacket,
    export_root: Path,
    adg_snapshot: Path,
) -> ScenarioValidationResult:
    spec = registered.spec
    trace_path = export_root / "traces" / f"{spec.app_id}_trace.json"
    # BUG-FIX (2026-04-26): pass the TRUSTED packet_path (derived from the
    # registered scenario, not the loaded packet) so a tampered packet
    # cannot redirect the hash check to a non-existent path and slip past.
    trusted_packet_path = (
        export_root / "contracts" / spec.app_id / spec.scenario_id
        / "evidence_packet.json"
    )
    return ScenarioValidationResult(
        app_id=spec.app_id,
        scenario_id=spec.scenario_id,
        trace_verdict=validate_trace_tree(trace_path),
        replay_verdict=validate_replay(
            registered=registered, export_root=export_root, adg_snapshot=adg_snapshot,
        ),
        inventory_verdict=validate_artifact_inventory(
            packet=packet, export_root=export_root,
            packet_path=trusted_packet_path,
        ),
    )


__all__ = [
    "Verdict",
    "ScenarioValidationResult",
    "validate_trace_tree",
    "validate_replay",
    "validate_artifact_inventory",
    "validate_scenario",
]
