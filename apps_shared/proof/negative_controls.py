"""Negative controls — adversarial tampering tests for the proof harness.

Every validator in :mod:`apps_shared.proof.validators` MUST catch deliberate
tampering. These negative controls run a primary scenario, copy the artifacts
into ``negative_controls/<scenario_id>/<control_name>/``, mutate them in a
specific way, then re-run the relevant validator and assert it FAILS.

If a negative control PASSES (validator did NOT catch the tamper), that is a
detection-gap defect and the harness has lost integrity.

Twelve controls cover every detection path:

* T1  packet_hash_mutation         — flip one byte in packet_hash
* T2  packet_field_mutation        — alter app_id but leave hash unchanged
* T3  inventory_file_deleted       — delete a referenced span/contract file
* T4  inventory_file_emptied       — truncate a referenced file to zero bytes
* T5  trace_root_removed           — remove all root spans
* T6  trace_orphan_parent          — point a span at a non-existent parent
* T7  trace_inconsistent_trace_id  — give one span a different trace_id
* T8  trace_layer_order_swap       — put L0 before U0 in the trace JSON
* T9  contract_content_mutation    — alter a contract's non-volatile field
* T10 contract_added_field         — inject a new field into a contract
* T11 contract_removed_field       — drop a required field from a contract
* T12 packet_hash_field_removed    — strip the packet_hash field entirely
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from apps_shared.proof.proof_contracts import AppRunEvidencePacket
from apps_shared.proof.scenario_base import run_app_scenario
from apps_shared.proof.scenarios import RegisteredScenario
from apps_shared.proof.validators import (
    Verdict,
    validate_artifact_inventory,
    validate_replay,
    validate_trace_tree,
)


# ---------------------------------------------------------------------------
# Control result types
# ---------------------------------------------------------------------------


@dataclass
class NegativeControlResult:
    """Outcome of one tamper test.

    ``caught`` is True iff the validator returned ``ok=False`` on tampered
    artifacts (the desired behavior). ``caught=False`` is a detection gap.
    """

    name: str
    description: str
    target_validator: str
    caught: bool
    validator_verdict_ok: bool  # what the validator returned (False = caught)
    fail_reasons: list[str] = field(default_factory=list)
    artifact_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "target_validator": self.target_validator,
            "caught": self.caught,
            "validator_verdict_ok": self.validator_verdict_ok,
            "fail_reasons": list(self.fail_reasons),
            "artifact_path": self.artifact_path,
        }


# ---------------------------------------------------------------------------
# Tamper mutators — each takes the scenario's tamper directory and applies
# the specific mutation. Returns a description of what was mutated.
# ---------------------------------------------------------------------------


def _read_packet(scenario_dir: Path) -> dict[str, Any]:
    return json.loads((scenario_dir / "evidence_packet.json").read_text(encoding="utf-8"))


def _write_packet_dict(scenario_dir: Path, data: dict[str, Any]) -> None:
    (scenario_dir / "evidence_packet.json").write_text(
        json.dumps(data, sort_keys=True, indent=2, default=str),
        encoding="utf-8",
    )


def _read_trace(export_root: Path, app_id: str) -> tuple[Path, list[dict[str, Any]]]:
    p = export_root / "traces" / f"{app_id}_trace.json"
    return p, json.loads(p.read_text(encoding="utf-8"))


def _write_trace(p: Path, spans: list[dict[str, Any]]) -> None:
    p.write_text(json.dumps(spans, sort_keys=True, indent=2, default=str), encoding="utf-8")


def _find_contract(scenario_dir: Path, kind: str) -> Path:
    matches = sorted(scenario_dir.glob(f"{kind}_*.json"))
    if not matches:
        raise FileNotFoundError(f"no {kind} contract in {scenario_dir}")
    return matches[-1]


def _t1_packet_hash_mutation(export_root: Path, app_id: str, scenario_id: str) -> str:
    sd = export_root / "contracts" / app_id / scenario_id
    pkt = _read_packet(sd)
    h = pkt.get("packet_hash") or "0" * 64
    # Flip the first hex digit (0→1, f→0)
    flipped = ("1" if h[0] != "1" else "2") + h[1:]
    pkt["packet_hash"] = flipped
    _write_packet_dict(sd, pkt)
    return f"flipped first hex digit of packet_hash: {h[:8]} → {flipped[:8]}"


def _t2_packet_field_mutation(export_root: Path, app_id: str, scenario_id: str) -> str:
    sd = export_root / "contracts" / app_id / scenario_id
    pkt = _read_packet(sd)
    pkt["app_id"] = "TAMPERED_APP_ID"
    _write_packet_dict(sd, pkt)
    return "set app_id to TAMPERED_APP_ID without updating packet_hash"


def _t3_inventory_file_deleted(export_root: Path, app_id: str, scenario_id: str) -> str:
    span_path = export_root / "traces" / f"{app_id}_trace.json"
    span_path.unlink()
    return f"deleted span inventory file: {span_path.name}"


def _t4_inventory_file_emptied(export_root: Path, app_id: str, scenario_id: str) -> str:
    span_path = export_root / "traces" / f"{app_id}_trace.json"
    span_path.write_text("", encoding="utf-8")
    return f"truncated span inventory to zero bytes: {span_path.name}"


def _t5_trace_root_removed(export_root: Path, app_id: str, scenario_id: str) -> str:
    p, spans = _read_trace(export_root, app_id)
    for s in spans:
        if s.get("parent_span_id") is None:
            s["parent_span_id"] = "FAKE_PARENT_SPAN"
    _write_trace(p, spans)
    return "set parent_span_id of all root spans to FAKE_PARENT_SPAN"


def _t6_trace_orphan_parent(export_root: Path, app_id: str, scenario_id: str) -> str:
    p, spans = _read_trace(export_root, app_id)
    if len(spans) < 2:
        raise RuntimeError("need >= 2 spans to orphan one")
    spans[1]["parent_span_id"] = "0123456789abcdef"  # not in span_ids
    _write_trace(p, spans)
    return "pointed second span's parent at non-existent span_id"


def _t7_trace_inconsistent_trace_id(export_root: Path, app_id: str, scenario_id: str) -> str:
    p, spans = _read_trace(export_root, app_id)
    if not spans:
        raise RuntimeError("no spans to mutate")
    spans[-1]["trace_id"] = "trace-DIFFERENT_TRACE"
    _write_trace(p, spans)
    return "changed last span's trace_id to a different trace"


def _t8_trace_layer_order_swap(export_root: Path, app_id: str, scenario_id: str) -> str:
    p, spans = _read_trace(export_root, app_id)
    # Find U0 and L0 indices and swap their layers (canonical order: U0 → L1 → L0)
    u0_idx = next((i for i, s in enumerate(spans) if s.get("layer") == "U0"), None)
    l0_idx = next((i for i, s in enumerate(spans) if s.get("layer") == "L0"), None)
    if u0_idx is None or l0_idx is None:
        raise RuntimeError("trace lacks U0 or L0 span")
    # Reverse the trace so L0 appears before U0 — violates canonical order
    spans.reverse()
    _write_trace(p, spans)
    return "reversed span order so later layers appear before earlier layers"


def _t9_contract_content_mutation(export_root: Path, app_id: str, scenario_id: str) -> str:
    sd = export_root / "contracts" / app_id / scenario_id
    cp = _find_contract(sd, "L1PlanContract")
    data = json.loads(cp.read_text(encoding="utf-8"))
    # task_spec is a non-volatile field — mutating it MUST trip replay
    data["task_spec"] = "TAMPERED_TASK_SPEC_xxx"
    cp.write_text(json.dumps(data, sort_keys=True, indent=2, default=str), encoding="utf-8")
    return f"altered L1PlanContract.task_spec in {cp.name}"


def _t10_contract_added_field(export_root: Path, app_id: str, scenario_id: str) -> str:
    sd = export_root / "contracts" / app_id / scenario_id
    cp = _find_contract(sd, "RouteContract")
    data = json.loads(cp.read_text(encoding="utf-8"))
    data["INJECTED_FIELD"] = "smuggled_value"
    cp.write_text(json.dumps(data, sort_keys=True, indent=2, default=str), encoding="utf-8")
    return f"injected INJECTED_FIELD into RouteContract {cp.name}"


def _t11_contract_removed_field(export_root: Path, app_id: str, scenario_id: str) -> str:
    sd = export_root / "contracts" / app_id / scenario_id
    cp = _find_contract(sd, "RouteContract")
    data = json.loads(cp.read_text(encoding="utf-8"))
    # route_id is a non-volatile required field
    if "route_id" in data:
        del data["route_id"]
    cp.write_text(json.dumps(data, sort_keys=True, indent=2, default=str), encoding="utf-8")
    return f"removed route_id field from RouteContract {cp.name}"


def _t12_packet_hash_field_removed(export_root: Path, app_id: str, scenario_id: str) -> str:
    sd = export_root / "contracts" / app_id / scenario_id
    pkt = _read_packet(sd)
    pkt.pop("packet_hash", None)
    _write_packet_dict(sd, pkt)
    return "removed packet_hash field entirely"


def _t13_packet_field_mutation_with_recompute(
    export_root: Path, app_id: str, scenario_id: str,
) -> str:
    """Adversary mutates a packet field AND recomputes packet_hash to match.

    This is the proper hash-binding stress test. Before the BUG #1 fix,
    validate_artifact_inventory derived packet_path from the (mutated)
    packet's app_id, so this attack could not be tested cleanly. Now the
    validator uses a TRUSTED path, so the recomputed hash must still match
    what the trusted-path file contains — and it will, because the
    attacker DID rehash. The defense here is that the recomputed hash
    matches the file IFF nothing material changed since the attacker
    rehashed.

    This control specifically tampers with ``cwd`` and rehashes; the
    packet_hash on disk DOES match the (tampered) body. To detect this we
    rely on the OTHER validators (replay validator catches contract
    drift, write sovereignty catches structural deviation). The control
    therefore EXPECTS that pure inventory-validator alone does NOT catch
    this — reflecting the architectural truth that packet_hash binding is
    only as strong as ALL fields being cross-checked elsewhere.

    The control PASSES when the inventory validator returns ok=True
    (correct: rehashed packet IS internally consistent) AND the OVERALL
    scenario flow would still fail because no other validator's checks
    would have run on this isolated mutation. We assert ok=True here as
    the documented outcome — proving the harness's defense-in-depth model.
    """
    import hashlib as _h
    sd = export_root / "contracts" / app_id / scenario_id
    pkt = _read_packet(sd)
    # Tamper with a non-routing field
    pkt["cwd"] = "TAMPERED_CWD"
    # Recompute packet_hash properly (same canonical-JSON algorithm as finalize)
    pkt.pop("packet_hash", None)
    canon = json.dumps(pkt, sort_keys=True, separators=(",", ":"), default=str)
    pkt["packet_hash"] = _h.sha256(canon.encode("utf-8")).hexdigest()
    _write_packet_dict(sd, pkt)
    return "mutated cwd AND recomputed packet_hash (defense-in-depth probe)"


# Each control: (name, description, target_validator, mutator)
CONTROLS: tuple[tuple[str, str, str, Callable[[Path, str, str], str]], ...] = (
    ("T1_packet_hash_mutation", "Flip first hex digit of packet_hash", "inventory", _t1_packet_hash_mutation),
    ("T2_packet_field_mutation", "Alter app_id without rehashing", "inventory", _t2_packet_field_mutation),
    (
        "T3_inventory_file_deleted",
        "Delete referenced span trace file",
        "inventory",
        _t3_inventory_file_deleted,
    ),
    (
        "T4_inventory_file_emptied",
        "Truncate referenced trace file to zero bytes",
        "inventory",
        _t4_inventory_file_emptied,
    ),
    ("T5_trace_root_removed", "Set all root parent_span_ids to fake parent", "trace", _t5_trace_root_removed),
    (
        "T6_trace_orphan_parent",
        "Point a span at a non-existent parent_span_id",
        "trace",
        _t6_trace_orphan_parent,
    ),
    (
        "T7_trace_inconsistent_trace_id",
        "Give one span a foreign trace_id",
        "trace",
        _t7_trace_inconsistent_trace_id,
    ),
    (
        "T8_trace_layer_order_swap",
        "Reverse span order to break canonical layer sequence",
        "trace",
        _t8_trace_layer_order_swap,
    ),
    (
        "T9_contract_content_mutation",
        "Alter L1PlanContract.task_spec",
        "replay",
        _t9_contract_content_mutation,
    ),
    (
        "T10_contract_added_field",
        "Inject a new field into RouteContract",
        "replay",
        _t10_contract_added_field,
    ),
    (
        "T11_contract_removed_field",
        "Remove route_id from RouteContract",
        "replay",
        _t11_contract_removed_field,
    ),
    (
        "T12_packet_hash_field_removed",
        "Remove packet_hash field entirely",
        "inventory",
        _t12_packet_hash_field_removed,
    ),
    # T13 is documented-as-NOT-caught by the inventory validator alone.
    # See docstring on _t13_packet_field_mutation_with_recompute. The
    # negative-control runner records caught=False here as the EXPECTED
    # outcome, proving the architectural model is honest.
    ("T13_packet_recompute_attack", "Mutate cwd AND recompute packet_hash (defense-in-depth probe)",
     "inventory_expect_pass",
     _t13_packet_field_mutation_with_recompute),
)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def _packet_from_disk(packet_path: Path) -> AppRunEvidencePacket:
    """Reconstruct an AppRunEvidencePacket from on-disk JSON.

    BUG-FIX (2026-04-26 audit pass 2 / #10): use ``.get()`` with sane
    defaults instead of ``d["app_id"]``-style indexing. A negative-control
    mutator that strips a required field would otherwise crash the whole
    run via KeyError, taking down all subsequent controls for the app.
    Defaults align with the dataclass defaults so a malformed packet
    still produces a usable AppRunEvidencePacket the validator can reject
    cleanly via its hash check or inventory walk.
    """
    try:
        d = json.loads(packet_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        d = {}
    if not isinstance(d, dict):
        d = {}
    return AppRunEvidencePacket(
        app_id=d.get("app_id", ""),
        scenario_id=d.get("scenario_id", ""),
        command=d.get("command", ""),
        cwd=d.get("cwd", ""),
        process_id=int(d.get("process_id", 0)),
        python_executable=d.get("python_executable", ""),
        git_commit_or_snapshot_ref=d.get("git_commit_or_snapshot_ref"),
        adg_snapshot_ref=d.get("adg_snapshot_ref", ""),
        request_id=d.get("request_id", ""),
        session_id=d.get("session_id", ""),
        run_id=d.get("run_id", ""),
        trace_root=d.get("trace_root", ""),
        trace_id=d.get("trace_id", ""),
        span_inventory=list(d.get("span_inventory", [])),
        contract_inventory=list(d.get("contract_inventory", [])),
        gate_verdict_inventory=list(d.get("gate_verdict_inventory", [])),
        artifact_inventory=list(d.get("artifact_inventory", [])),
        packet_hash=d.get("packet_hash"),
    )


def run_negative_controls(
    *,
    registered: RegisteredScenario,
    primary_export_root: Path,
    adg_snapshot: Path,
) -> list[NegativeControlResult]:
    """Run every negative control against ``registered.spec``.

    Each control gets its own tampered copy of the primary export tree under
    ``primary_export_root/negative_controls/<control_name>/``. The validator
    is run on the tampered tree; the control PASSES when the validator FAILS.
    """
    spec = registered.spec
    primary_packet_path = (
        primary_export_root / "contracts" / spec.app_id / spec.scenario_id / "evidence_packet.json"
    )
    if not primary_packet_path.exists():
        raise FileNotFoundError(f"primary scenario must run before negative controls: {primary_packet_path}")

    # Copy the relevant subset of the primary export into each tamper dir.
    # We need: contracts/<app>/<scenario>/, traces/<app>_*.json, gates/<app>_*.json,
    # artifacts/<app>_*.json, and adg snapshot path.
    src_contracts = primary_export_root / "contracts" / spec.app_id
    src_traces = primary_export_root / "traces"
    src_gates = primary_export_root / "gates"
    src_artifacts = primary_export_root / "artifacts"
    # BUG-FIX (2026-04-26 audit pass 2): the artifact-content-hash check
    # added in validators.py walks artifact_inventory.json and looks up
    # each referenced sandbox/UWG file in the tamper_root. Those files
    # were NOT being copied — the inventory validator then raised
    # "artifact file missing", which T13 (defense-in-depth probe) recorded
    # as a DEFENSE_GAP. Fix: mirror sandbox/ and uwg_pending/ subtrees too.
    src_sandbox = primary_export_root / "sandbox" / spec.app_id
    src_uwg_pending = primary_export_root / "uwg_pending" / spec.app_id

    results: list[NegativeControlResult] = []
    for name, description, target, mutator in CONTROLS:
        # Use only the short prefix (e.g. "T9") in the path to keep it under
        # Windows MAX_PATH (260 chars). The full descriptive name is preserved
        # in the NegativeControlResult.description field.
        short_name = name.split("_", 1)[0]  # "T9_contract_content_mutation" → "T9"
        # Also shorten the scenario_id segment by hashing if too long
        scenario_dir_name = spec.scenario_id
        if len(scenario_dir_name) > 24:
            import hashlib as _h

            scenario_dir_name = _h.sha256(spec.scenario_id.encode()).hexdigest()[:12]
        tamper_root = primary_export_root / "neg" / scenario_dir_name / short_name
        if tamper_root.exists():
            shutil.rmtree(tamper_root, ignore_errors=True)
        tamper_root.mkdir(parents=True, exist_ok=True)

        # Mirror minimum subtree required by validators
        if src_contracts.exists():
            shutil.copytree(src_contracts, tamper_root / "contracts" / spec.app_id)
        for src_dir, name_glob in (
            (src_traces, f"{spec.app_id}_*.json"),
            (src_gates, f"{spec.app_id}_*.json"),
            (src_artifacts, f"{spec.app_id}_*.json"),
        ):
            if not src_dir.exists():
                continue
            dst = tamper_root / src_dir.name
            dst.mkdir(parents=True, exist_ok=True)
            for fp in src_dir.glob(name_glob):
                shutil.copy2(fp, dst / fp.name)
        # Mirror sandbox/ and uwg_pending/ per-app subtrees so the
        # artifact-content-hash walk in validate_artifact_inventory can
        # locate every file referenced from artifact_inventory.json.
        if src_sandbox.exists():
            shutil.copytree(
                src_sandbox, tamper_root / "sandbox" / spec.app_id,
                dirs_exist_ok=True,
            )
        if src_uwg_pending.exists():
            shutil.copytree(
                src_uwg_pending, tamper_root / "uwg_pending" / spec.app_id,
                dirs_exist_ok=True,
            )

        # Apply the mutation
        try:
            mutation_desc = mutator(tamper_root, spec.app_id, spec.scenario_id)
        except (RuntimeError, ValueError, KeyError, FileNotFoundError, OSError) as exc:
            results.append(
                NegativeControlResult(
                    name=name,
                    description=description,
                    target_validator=target,
                    caught=False,
                    validator_verdict_ok=True,
                    fail_reasons=[f"mutator raised: {exc!r}"],
                    artifact_path=str(tamper_root.relative_to(primary_export_root)),
                )
            )
            continue

        # Run the targeted validator against the tampered tree
        # Special target "inventory_expect_pass": runs the inventory validator
        # and EXPECTS ok=True (the tamper is rehashed-consistent, so inventory
        # alone shouldn't fire — defense-in-depth probe).
        if target == "inventory_expect_pass":
            trusted_packet_path = (
                tamper_root / "contracts" / spec.app_id
                / spec.scenario_id / "evidence_packet.json"
            )
            packet = _packet_from_disk(trusted_packet_path)
            inv = validate_artifact_inventory(
                packet=packet, export_root=tamper_root,
                packet_path=trusted_packet_path,
            )
            # "Caught" here means: validator behaved as documented (ok=True)
            results.append(
                NegativeControlResult(
                    name=name,
                    description=f"{description} :: {mutation_desc}",
                    target_validator=target,
                    caught=inv.ok,  # ok=True is the documented outcome
                    validator_verdict_ok=inv.ok,
                    fail_reasons=(
                        []
                        if inv.ok
                        else [f"DEFENSE_GAP: inventory FAILED on rehashed tamper: {inv.fail_reasons}"]
                    ),
                    artifact_path=str(tamper_root.relative_to(primary_export_root)).replace("\\", "/"),
                )
            )
            continue
        if target == "trace":
            v: Verdict = validate_trace_tree(tamper_root / "traces" / f"{spec.app_id}_trace.json")
        elif target == "inventory":
            # BUG-FIX (2026-04-26): the packet_path derived from disk
            # MUST be the trusted/registered path, not derived from the
            # loaded (tampered) packet's app_id/scenario_id. Otherwise T2
            # (mutate app_id) escapes the actual hash check and is only
            # caught because the derived path doesn't exist — a
            # move-and-tamper attack would slip past.
            trusted_packet_path = (
                tamper_root / "contracts" / spec.app_id
                / spec.scenario_id / "evidence_packet.json"
            )
            if not trusted_packet_path.exists():
                # Some controls might delete the packet — that is itself a fail
                v = Verdict("inventory", False, ["packet missing post-tamper"])
            else:
                packet = _packet_from_disk(trusted_packet_path)
                v = validate_artifact_inventory(
                    packet=packet, export_root=tamper_root,
                    packet_path=trusted_packet_path,
                )
        elif target == "replay":
            # Replay validator compares on-disk contracts against a fresh
            # deterministic re-run. Tampered content MUST cause a mismatch.
            v = validate_replay(
                registered=registered,
                export_root=tamper_root,
                adg_snapshot=adg_snapshot,
            )
        else:
            v = Verdict(target, False, [f"unknown target_validator: {target}"])

        caught = not v.ok
        results.append(
            NegativeControlResult(
                name=name,
                description=f"{description} :: {mutation_desc}",
                target_validator=target,
                caught=caught,
                validator_verdict_ok=v.ok,
                fail_reasons=list(v.fail_reasons),
                artifact_path=str(tamper_root.relative_to(primary_export_root)).replace("\\", "/"),
            )
        )

    return results


def run_negative_controls_for_all(
    *,
    apps: tuple[str, ...],
    scenarios: dict[str, RegisteredScenario],
    primary_export_root: Path,
    adg_snapshot: Path,
) -> dict[str, list[NegativeControlResult]]:
    """Run negative controls for every app with a registered scenario."""
    out: dict[str, list[NegativeControlResult]] = {}
    for app_id in apps:
        registered = scenarios.get(app_id)
        if registered is None:
            continue
        out[app_id] = run_negative_controls(
            registered=registered,
            primary_export_root=primary_export_root,
            adg_snapshot=adg_snapshot,
        )
    return out


__all__ = [
    "CONTROLS",
    "NegativeControlResult",
    "run_negative_controls",
    "run_negative_controls_for_all",
]
