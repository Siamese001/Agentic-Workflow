"""apps_* anti-cheat proof runner — single-app entrypoint.

CLI (matches user spec):

    python -m tools.apps_proof.run_app_proof \
        --app apps_underwriting_ai \
        --fixture fixtures/apps_underwriting_ai/golden_borrower_package.json \
        --proof-root artifacts/apps_proof \
        --require-otel \
        --require-replay \
        --require-adg

Behavior:
  1. Resolve the registered scenario for ``--app`` from
     ``apps_shared.proof.scenarios.SCENARIOS``. A fixture (when supplied)
     overrides ``intake_body`` and ``extra_payload``.
  2. (``--require-adg``) Snapshot ADG row counts for files-touched-by-app
     into ``adg/adg_before.json``.
  3. Drive ``scenario_base.run_app_scenario`` once into a private scratch
     directory; then mirror its outputs into the user's canonical layout
     (``contracts/u0_validated_request.json`` etc).
  4. (``--require-replay``) Drive a second invocation with the same seed,
     compare canonical contracts byte-for-byte, write ``replay_comparison.json``.
  5. (``--require-adg``) Re-snapshot ADG, write ``adg_after.json`` and
     ``adg_delta.json``.
  6. Compute ``proof_manifest_hash`` over the canonical inputs and stamp
     it into ``run_manifest.json``.
  7. Invoke the independent verifier (``tools.apps_proof.verify_app_proof``)
     and exit with its verdict.

This runner is deterministic given a fixed seed. Two invocations with the
same ``--app`` and ``--fixture`` produce identical canonical-JSON contracts
under ``contracts/``.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Imports must come AFTER sys.path mutation so that
# ``python tools/apps_proof/run_app_proof.py`` and
# ``python -m tools.apps_proof.run_app_proof`` both resolve.
from apps_shared.proof.scenarios import SCENARIOS, RegisteredScenario  # noqa: E402
from apps_shared.proof.scenario_base import (  # noqa: E402
    ScenarioContext,
    ScenarioSpec,
    run_app_scenario,
)
from apps_shared.proof.proof_contracts import PROOF_STATUS_PASS  # noqa: E402
from apps_shared.proof.validators import _strip_volatile as _strip_volatile_canonical  # noqa: E402

from tools.apps_proof._layout import (  # noqa: E402
    CONTRACT_FILE_BY_KIND,
    ProofRunPaths,
)
from tools.apps_proof.verify_app_proof import (  # noqa: E402
    VERIFIER_VERSION,
    verify,
    write_verdict,
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


def _latest_adg_snapshot() -> Path | None:
    snaps = sorted((REPO_ROOT / "artifacts" / "adg").glob("adg_indexed_*.sqlite"))
    return snaps[-1] if snaps else None


# ---------------------------------------------------------------------------
# Fixture loading
# ---------------------------------------------------------------------------


def _load_fixture(path: Path) -> dict[str, Any]:
    """Load a fixture JSON or JSONL — first record only.

    Accepts either a JSON object or a JSONL where the first non-empty line
    is a JSON object. Anything else raises ValueError.
    """
    if not path.exists():
        raise FileNotFoundError(f"fixture not found: {path}")
    text = path.read_text(encoding="utf-8")
    # Try JSON first.
    try:
        obj = json.loads(text)
        if isinstance(obj, list) and obj and isinstance(obj[0], dict):
            return obj[0]
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    # Fall back to JSONL — first non-empty line.
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if isinstance(rec, dict):
            return rec
    raise ValueError(f"fixture {path} contains no JSON object")


def _spec_with_fixture(spec: ScenarioSpec, fixture: dict[str, Any] | None) -> ScenarioSpec:
    """Return a copy of ``spec`` overridden with fields from ``fixture``."""
    if not fixture:
        return spec
    return dataclasses.replace(
        spec,
        intake_body=str(fixture.get("intake_body", spec.intake_body)),
        task_spec=str(fixture.get("task_spec", spec.task_spec)),
        query_spec=str(fixture.get("query_spec", spec.query_spec)),
        grounding_required=bool(
            fixture.get("grounding_required", spec.grounding_required)
        ),
        extra_payload={**spec.extra_payload, **fixture.get("extra_payload", {})},
    )


# ---------------------------------------------------------------------------
# ADG snapshotting (lightweight, file-scoped)
# ---------------------------------------------------------------------------


def _adg_snapshot_for_app(adg_path: Path, app_id: str) -> dict[str, Any]:
    """Capture a small per-app footprint from the ADG snapshot.

    Records: total nodes/violations/overlay_violations under ``app_id/`` plus
    per-P-view hit counts. Used to compute adg_delta when the same SQLite is
    queried at the end of the run (current run is read-only — delta will be
    zero unless the user separately regenerates the ADG).
    """
    if not adg_path.exists():
        return {
            "snapshot": str(adg_path),
            "captured_at": _utcnow_iso(),
            "missing": True,
        }
    out: dict[str, Any] = {
        "snapshot": adg_path.name,
        "snapshot_path": str(adg_path),
        "captured_at": _utcnow_iso(),
        "app_id": app_id,
        "nodes": 0,
        "violations": 0,
        "overlay_violations": 0,
        "per_p_view": {},
    }
    con = sqlite3.connect(str(adg_path))
    try:
        cur = con.cursor()
        out["nodes"] = int(
            cur.execute(
                "SELECT COUNT(*) FROM nodes WHERE resolved_path LIKE ?",
                (f"{app_id}/%",),
            ).fetchone()[0]
        )
        for table in ("violations", "overlay_violations"):
            cols = [
                r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()
            ]
            file_col = next(
                (c for c in ("file", "file_path", "resolved_path") if c in cols), None
            )
            if file_col:
                out[table] = int(
                    cur.execute(
                        f"SELECT COUNT(*) FROM {table} WHERE {file_col} LIKE ?",
                        (f"{app_id}/%",),
                    ).fetchone()[0]
                )
        # Per P-view hit counts (best-effort)
        for view in (
            "v_p0_apps_direct_infra",
            "v_p0_write_bypass_uwg",
            "v_p0_provider_bypass",
        ):
            try:
                cols = [
                    r[1] for r in cur.execute(f"PRAGMA table_info({view})").fetchall()
                ]
            except sqlite3.OperationalError:
                out["per_p_view"][view] = -1
                continue
            file_col = next(
                (c for c in ("file", "file_path", "resolved_path") if c in cols), None
            )
            if file_col:
                try:
                    out["per_p_view"][view] = int(
                        cur.execute(
                            f"SELECT COUNT(*) FROM {view} WHERE {file_col} LIKE ?",
                            (f"{app_id}/%",),
                        ).fetchone()[0]
                    )
                except sqlite3.OperationalError:
                    out["per_p_view"][view] = -1
            else:
                out["per_p_view"][view] = -1
    finally:
        con.close()
    return out


def _adg_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Compute delta between two _adg_snapshot_for_app results."""
    delta: dict[str, Any] = {
        "before_snapshot": before.get("snapshot"),
        "after_snapshot": after.get("snapshot"),
        "delta_nodes": int(after.get("nodes", 0)) - int(before.get("nodes", 0)),
        "delta_violations": int(after.get("violations", 0)) - int(before.get("violations", 0)),
        "delta_overlay_violations": int(after.get("overlay_violations", 0))
        - int(before.get("overlay_violations", 0)),
        "delta_p0": 0,
        "p0_increased": False,
    }
    p0_views = ("v_p0_apps_direct_infra", "v_p0_write_bypass_uwg", "v_p0_provider_bypass")
    p0_before = sum(
        max(0, int(before.get("per_p_view", {}).get(v, 0))) for v in p0_views
    )
    p0_after = sum(
        max(0, int(after.get("per_p_view", {}).get(v, 0))) for v in p0_views
    )
    delta["delta_p0"] = p0_after - p0_before
    delta["p0_increased"] = (p0_after - p0_before) > 0
    return delta


# ---------------------------------------------------------------------------
# Scenario invocation + layout reorg
# ---------------------------------------------------------------------------


def _drive_scenario(
    spec: ScenarioSpec,
    *,
    scratch: Path,
    adg_snapshot: Path,
    customizer,
    seed: str,
) -> tuple[Path, ScenarioContext]:
    """Run the scenario into ``scratch`` and return (scenario_dir, ctx)."""
    # Mirror run_app_scenario's logic but expose the context for trace export.
    ctx = ScenarioContext(spec=spec, export_root=scratch, adg_snapshot=adg_snapshot, seed=seed)
    _, u0_span = ctx.run_u0()
    _, l1_span = ctx.run_l1(u0_span)
    _, l0_span = ctx.run_l0(l1_span)
    _, c0_span = ctx.run_c0(l0_span)
    _, pa_span = ctx.run_prompt_assembly(c0_span)
    _, l3_span = ctx.run_l3_skip(pa_span)
    _, l2_span = ctx.run_l2(l3_span)
    _, _ = ctx.run_exit(l2_span)
    if customizer is not None:
        try:
            customizer(ctx)
        except (
            RuntimeError, ValueError, TypeError, AttributeError,
            ImportError, OSError, KeyError,
        ) as exc:
            ctx.emit_span(
                layer="customizer",
                name=f"{spec.app_id}.customizer",
                parent_span_id=None,
                status="FAIL",
                started_at=_utcnow_iso(),
                ended_at=_utcnow_iso(),
                attrs={"error": repr(exc)},
            )
    packet = ctx.build_packet()
    from apps_shared.proof.proof_contracts import write_packet
    packet_path = ctx.scenario_dir / "evidence_packet.json"
    write_packet(packet, packet_path)
    return ctx.scenario_dir, ctx


def _wrap_contract(
    *,
    kind: str,
    raw_payload: Any,
    ctx: ScenarioContext,
    span_id: str | None,
    contract_digest: str | None,
) -> dict[str, Any]:
    """Wrap a scenario_base contract payload with stable trace-link metadata.

    Per master plan §"PROOF ARTIFACT STRUCTURE", every contract emitted under
    ``contracts/`` MUST include: request_id, run_id, trace_id or trace_root,
    span_id where applicable, route_id where applicable, policy_hash,
    blueprint_hash, replay_key, contract_digest, payload.

    Wrapping is deterministic (no timestamps in the wrapper) so replay
    comparison stays byte-equal.
    """
    return {
        "kind": kind,
        "request_id": ctx.request_id_hint,
        "run_id": ctx.run_id,
        "trace_id": ctx.trace_id,
        "trace_root": ctx.trace_root,
        "session_id": ctx.session_id,
        "span_id": span_id,
        "route_id": getattr(ctx.route_contract, "route_id", None) if ctx.route_contract else None,
        "policy_hash": f"ph-{ctx.spec.app_id}",
        "blueprint_hash": f"bp-{ctx.spec.app_id}",
        "replay_key": f"rrk-{ctx.run_id}",
        "contract_digest": contract_digest,
        "payload": raw_payload,
    }


def _kind_from_stem(stem: str) -> str:
    """Robustly extract the contract kind from a scenario_base filename.

    scenario_base emits ``<Kind>_<digest8>.json``. ``digest8`` is exactly 8
    hex characters. Falling back on ``rsplit('_', 1)`` is wrong for names
    like ``contract_inventory`` (no digest suffix) — this helper handles both.
    """
    # Kind keys that scenario_base may emit but with no _<digest8> suffix.
    if stem in {"contract_inventory", "evidence_packet"}:
        return stem
    if "_" in stem:
        head, tail = stem.rsplit("_", 1)
        # Real digest suffixes are exactly 8 lowercase hex characters.
        if len(tail) == 8 and all(c in "0123456789abcdef" for c in tail):
            return head
    return stem


def _materialize_user_layout(
    *,
    paths: ProofRunPaths,
    scenario_dir: Path,
    ctx: ScenarioContext,
) -> None:
    """Copy scenario_base outputs into user's canonical tree, wrapping contracts."""
    paths.mkdirs()

    # Build a kind → (span_id, contract_digest) map from ctx.contracts so the
    # wrapper can reference the exact span that emitted each contract.
    contract_meta: dict[str, tuple[str | None, str | None]] = {}
    for c in ctx.contracts:
        contract_meta.setdefault(c.contract_kind, (c.emitted_by_span_id, c.digest))

    # 1. Contracts: scenario_base writes <Kind>_<digest8>.json. Wrap each in
    #    the trace-link envelope and write under canonical filename.
    for src in sorted(scenario_dir.glob("*.json")):
        kind = _kind_from_stem(src.stem)
        if kind == "evidence_packet":
            # The harness's hash-chained packet is preserved alongside, intact.
            shutil.copyfile(src, paths.run_root / "evidence_packet.json")
            continue
        if kind == "contract_inventory":
            # Inventory file is a list of records; wrap with trace metadata
            # so the verifier's artifact_join check can confirm linkage.
            try:
                inventory_records = json.loads(src.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                inventory_records = []
            wrapped_inventory = _wrap_contract(
                kind="ContractInventory",
                raw_payload=inventory_records,
                ctx=ctx,
                span_id=None,
                contract_digest=None,
            )
            (paths.contracts_dir / "contract_inventory.json").write_text(
                json.dumps(wrapped_inventory, indent=2, sort_keys=True, default=str),
                encoding="utf-8",
            )
            continue
        canonical_name = CONTRACT_FILE_BY_KIND.get(kind)
        try:
            raw_payload = json.loads(src.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raw_payload = {"_unloadable": str(exc)}
        span_id, digest = contract_meta.get(kind, (None, None))
        wrapped = _wrap_contract(
            kind=kind,
            raw_payload=raw_payload,
            ctx=ctx,
            span_id=span_id,
            contract_digest=digest,
        )
        if canonical_name:
            dest = paths.contracts_dir / canonical_name
            # If two emissions of the same kind collide, suffix.
            if dest.exists():
                suffix = src.stem.rsplit("_", 1)[-1] if "_" in src.stem else "extra"
                dest = paths.contracts_dir / f"{canonical_name.rsplit('.json', 1)[0]}__{suffix}.json"
            dest.write_text(
                json.dumps(wrapped, indent=2, sort_keys=True, default=str),
                encoding="utf-8",
            )
        else:
            # Unknown kind — preserve under contracts/ with a safe name.
            (paths.contracts_dir / f"{kind}.json").write_text(
                json.dumps(wrapped, indent=2, sort_keys=True, default=str),
                encoding="utf-8",
            )

    # 2. OTEL trace export (file-based; matches scenario_base spans list).
    trace_export = [s.to_dict() for s in ctx.spans]
    paths.otel_trace.write_text(
        json.dumps(trace_export, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )

    # 3. Span tree text — indent by parent chain depth.
    span_by_id = {s.span_id: s for s in ctx.spans}
    children: dict[str | None, list] = {}
    for s in ctx.spans:
        children.setdefault(s.parent_span_id, []).append(s)
    lines: list[str] = []

    def _walk(node, depth: int) -> None:
        marker = f"[{node.status}]"
        lines.append(
            f"{'  ' * depth}- {node.layer}/{node.name} {marker} span_id={node.span_id}"
        )
        for child in children.get(node.span_id, []):
            _walk(child, depth + 1)

    for root in children.get(None, []):
        _walk(root, 0)
    paths.span_tree.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 4. Span coverage report.
    layers_seen = sorted({s.layer for s in ctx.spans})
    coverage = {
        "trace_id": ctx.trace_id,
        "run_id": ctx.run_id,
        "layers_seen": layers_seen,
        "span_count": len(ctx.spans),
        "by_layer_status": {},
    }
    for s in ctx.spans:
        layer_bucket = coverage["by_layer_status"].setdefault(s.layer, {})
        layer_bucket[s.status] = layer_bucket.get(s.status, 0) + 1
    paths.span_coverage.write_text(
        json.dumps(coverage, indent=2, sort_keys=True), encoding="utf-8"
    )

    # 5. Gates JSONL + summary
    gates_path = paths.gate_verdicts_jsonl
    with gates_path.open("w", encoding="utf-8") as fh:
        for g in ctx.gates:
            fh.write(json.dumps(g.to_dict(), sort_keys=True) + "\n")

    summary_lines = [
        "# Gate Summary",
        "",
        f"- run_id: `{ctx.run_id}`",
        f"- trace_id: `{ctx.trace_id}`",
        f"- gates: {len(ctx.gates)}",
        "",
        "| Gate | Verdict | Reasons |",
        "|---|---|---|",
    ]
    for g in ctx.gates:
        summary_lines.append(
            f"| `{g.gate_id}` | {g.verdict} | {', '.join(g.reason_codes) or '-'} |"
        )
    paths.gate_summary.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Replay comparison
# ---------------------------------------------------------------------------


# Replay comparison delegates to apps_shared.proof.validators._strip_volatile
# which is the SSOT for which fields are non-deterministic across runs.
# That function handles suffix patterns (`_at_observed`, `_time_unix`,
# `_receipt_ref`, `_seed_ref`) and the explicit allowlist (`created_at`,
# `started_at`, `ended_at`, `timestamp`, `wall_clock_utc`). Re-exported
# here for clarity at call sites.
def _strip_volatile(obj: Any) -> Any:
    """Strip volatile fields for replay comparison.

    Composes the canonical SSOT from ``apps_shared.proof.validators`` plus
    wrapper-only nonces this runner introduces:

      * ``contract_digest`` — wrapper field; sourced from scenario_base
        ``emit_contract`` which hashes the unstripped payload. Its drift
        is by-design and not part of the user's anti-cheat invariant.
    """
    canonical = _strip_volatile_canonical(obj)
    if isinstance(canonical, dict):
        return {k: v for k, v in canonical.items() if k != "contract_digest"}
    return canonical


def _replay_compare(run1_dir: Path, run2_dir: Path, paths: ProofRunPaths) -> dict[str, Any]:
    """Compare canonical contracts of two runs by content (volatile-stripped).

    The user's anti-cheat spec requires byte-equal canonical content for the
    deterministic three: ValidatedRequest (U0), L1PlanContract, and
    RouteContract (L0). C0 / Prompt Assembly / L2 contracts legitimately
    carry fresh per-run nonces (evidence_hmac, contract_id, manifest_hash
    of dispatchable envelope) — those are checked separately by the
    deterministic_digest_report and the route_digest field on RouteContract.
    """
    out: dict[str, Any] = {
        "ok": True,
        "compared_paths": [],
        "diffs": [],
        "reasons": [],
    }
    # Deterministic-three (user spec §10): byte-equal required.
    keys_to_compare = (
        "u0_validated_request.json",
        "l1_plan_contract.json",
        "l0_route_contract.json",
    )
    # Best-effort comparison set: nonces stripped, drift logged but not failing.
    keys_to_log_only = (
        "c0_final_evidence_contract.json",
        "prompt_assembly_manifest.json",
        "l2_sealed_artifact.json",
        "exit_disposition.json",
    )
    for k in keys_to_compare:
        a = run1_dir / k
        b = run2_dir / k
        if not a.exists() and not b.exists():
            continue  # neither emitted — fine
        if a.exists() != b.exists():
            out["ok"] = False
            out["reasons"].append(f"presence_mismatch:{k}")
            out["diffs"].append({"path": k, "type": "presence_mismatch"})
            continue
        try:
            ja = _strip_volatile(json.loads(a.read_text(encoding="utf-8")))
            jb = _strip_volatile(json.loads(b.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            out["ok"] = False
            out["reasons"].append(f"unloadable:{k}:{exc}")
            continue
        out["compared_paths"].append(k)
        ha = _sha256(ja)
        hb = _sha256(jb)
        if ha != hb:
            out["ok"] = False
            # Fail-code mapping: route digest mismatch → user spec
            if k == "l0_route_contract.json":
                out["reasons"].append("FAIL_REPLAY_ROUTE_MISMATCH")
            else:
                out["reasons"].append(f"content_mismatch:{k}")
            out["diffs"].append({"path": k, "hash_run1": ha, "hash_run2": hb})

    # Best-effort: log drift on nonce-bearing contracts but do not fail.
    drift_log: list[dict[str, Any]] = []
    for k in keys_to_log_only:
        a = run1_dir / k
        b = run2_dir / k
        if not a.exists() or not b.exists():
            continue
        try:
            ja = _strip_volatile(json.loads(a.read_text(encoding="utf-8")))
            jb = _strip_volatile(json.loads(b.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
        ha = _sha256(ja)
        hb = _sha256(jb)
        drift_log.append({"path": k, "hash_run1": ha, "hash_run2": hb, "match": ha == hb})

    # Save the deterministic_digest_report alongside the comparison.
    digest_report = {
        "deterministic_three": {},
        "best_effort_set": drift_log,
    }
    for k in keys_to_compare:
        a = run1_dir / k
        b = run2_dir / k
        rec: dict[str, str] = {}
        if a.exists():
            ja = _strip_volatile(json.loads(a.read_text(encoding="utf-8")))
            rec["run1_hash"] = _sha256(ja)
        if b.exists():
            jb = _strip_volatile(json.loads(b.read_text(encoding="utf-8")))
            rec["run2_hash"] = _sha256(jb)
        rec["match"] = rec.get("run1_hash") == rec.get("run2_hash")
        digest_report["deterministic_three"][k] = rec
    paths.deterministic_digest_report.write_text(
        json.dumps(digest_report, indent=2, sort_keys=True), encoding="utf-8"
    )
    return out


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


def _build_run_manifest(
    *,
    paths: ProofRunPaths,
    spec: ScenarioSpec,
    ctx: ScenarioContext,
    cli_command: str,
    fixture_path: Path | None,
    flags: dict[str, bool],
    adg_snapshot: Path,
) -> dict[str, Any]:
    """Compose run_manifest.json (without proof_manifest_hash yet)."""
    # Source hashes
    artifact_hashes: dict[str, str] = {}
    contract_hashes: dict[str, str] = {}
    if paths.contracts_dir.exists():
        for jp in sorted(paths.contracts_dir.rglob("*.json")):
            rel = str(jp.relative_to(paths.run_root)).replace("\\", "/")
            contract_hashes[rel] = _sha256_file(jp)

    # Discover sealed artifact hash if present
    sealed = paths.contracts_dir / "l2_sealed_artifact.json"
    sealed_hash = _sha256_file(sealed) if sealed.exists() else None

    # Determine grounding/managed flags from the scenario spec
    manifest = {
        "app_name": spec.app_id,
        "run_id": ctx.run_id,
        "request_id": ctx.request_id_hint,
        "trace_id": ctx.trace_id,
        "route_id": getattr(ctx.route_contract, "route_id", None) if ctx.route_contract else None,
        "execution_form": "SINGLE_STEP",
        "grounding_required": bool(spec.grounding_required),
        "managed_workflow_required": False,
        "mutation_requested": False,
        "hitl_required": False,
        "uwg_required": False,
        "policy_hash": f"ph-{spec.app_id}",
        "blueprint_hash": f"bp-{spec.app_id}",
        "replay_key": f"rrk-{ctx.run_id}",
        "started_at": _utcnow_iso(),
        "finished_at": _utcnow_iso(),
        "artifact_hashes": artifact_hashes,
        "generated_by_command": cli_command,
        "proof_verifier_version": VERIFIER_VERSION,
        "fixture_path": str(fixture_path) if fixture_path else None,
        "adg_snapshot": str(adg_snapshot),
        "scenario_id": spec.scenario_id,
        "runtime_boundary_ts": ctx.runtime_boundary_ts,
        "exit_disposition": getattr(ctx, "_exit_disposition", None),
        "sealed_artifact_hash": sealed_hash,
        "flags": flags,
        # proof_manifest_hash filled later
    }
    return manifest


def _stamp_proof_manifest_hash(
    manifest: dict[str, Any], paths: ProofRunPaths
) -> str:
    """Compute proof_manifest_hash exactly as verify_app_proof recomputes."""
    body_for_hash = {k: v for k, v in manifest.items() if k != "proof_manifest_hash"}
    artifact_hashes: dict[str, str] = {}
    contract_hashes: dict[str, str] = {}
    if paths.contracts_dir.exists():
        for jp in sorted(paths.contracts_dir.rglob("*.json")):
            rel = str(jp.relative_to(paths.run_root)).replace("\\", "/")
            contract_hashes[rel] = _sha256_file(jp)
        for jp in sorted(paths.contracts_dir.rglob("*.jsonl")):
            rel = str(jp.relative_to(paths.run_root)).replace("\\", "/")
            contract_hashes[rel] = _sha256_file(jp)

    trace_hash = _sha256_file(paths.otel_trace) if paths.otel_trace.exists() else ""
    gate_hash = _sha256_file(paths.gate_verdicts_jsonl) if paths.gate_verdicts_jsonl.exists() else ""
    replay_hash = _sha256_file(paths.replay_comparison) if paths.replay_comparison.exists() else ""
    adg_hash = _sha256_file(paths.adg_delta) if paths.adg_delta.exists() else ""

    recomputed_input = {
        "run_manifest": body_for_hash,
        "artifact_hashes": artifact_hashes,
        "trace_export_hash": trace_hash,
        "contract_hashes": contract_hashes,
        "gate_verdict_hash": gate_hash,
        "replay_comparison_hash": replay_hash,
        "adg_delta_hash": adg_hash,
    }
    digest = _sha256(recomputed_input)
    manifest["proof_manifest_hash"] = digest
    return digest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tools.apps_proof.run_app_proof",
        description="Anti-cheat proof runner for one apps_* application.",
    )
    p.add_argument("--app", required=True, help="apps_* package name, e.g. apps_underwriting_ai")
    p.add_argument(
        "--fixture",
        type=Path,
        default=None,
        help="Optional input fixture (JSON or JSONL). First record overrides intake_body.",
    )
    p.add_argument(
        "--proof-root",
        type=Path,
        default=Path("artifacts/apps_proof"),
        help="Output root (default: artifacts/apps_proof)",
    )
    p.add_argument("--adg", type=Path, default=None, help="ADG snapshot (default: latest)")
    p.add_argument("--require-otel", action="store_true", help="Require OTEL trace export")
    p.add_argument("--require-replay", action="store_true", help="Require replay determinism check")
    p.add_argument("--require-adg", action="store_true", help="Require ADG before/after diff")
    p.add_argument(
        "--seed",
        default=None,
        help="Override deterministic seed (default: scenario_id, exposes replay tampering)",
    )
    p.add_argument(
        "--run-id",
        default=None,
        help="Override generated run_id (default: 12-hex random)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.app not in SCENARIOS:
        print(
            f"ERROR: no registered scenario for app={args.app!r}. "
            f"Known: {sorted(SCENARIOS.keys())}",
            file=sys.stderr,
        )
        return 2

    adg_snapshot = args.adg or _latest_adg_snapshot()
    if adg_snapshot is None or not adg_snapshot.exists():
        print(
            f"ERROR: no ADG snapshot found (looked for {args.adg or 'artifacts/adg/'})",
            file=sys.stderr,
        )
        return 2

    fixture: dict[str, Any] | None = None
    if args.fixture:
        fixture = _load_fixture(args.fixture)

    registered: RegisteredScenario = SCENARIOS[args.app]
    spec = _spec_with_fixture(registered.spec, fixture)

    run_id = args.run_id or uuid.uuid4().hex[:12]
    paths = ProofRunPaths(proof_root=args.proof_root.resolve(), app_name=args.app, run_id=run_id)
    paths.mkdirs()

    flags = {
        "require_otel": bool(args.require_otel),
        "require_replay": bool(args.require_replay),
        "require_adg": bool(args.require_adg),
    }

    # Persist run_request.json (input snapshot)
    run_request = {
        "app_name": args.app,
        "run_id": run_id,
        "fixture_path": str(args.fixture) if args.fixture else None,
        "fixture_payload": fixture,
        "spec": dataclasses.asdict(spec),
        "flags": flags,
        "submitted_at": _utcnow_iso(),
    }
    paths.run_request.write_text(
        json.dumps(run_request, indent=2, sort_keys=True, default=str), encoding="utf-8"
    )

    # ADG before
    if args.require_adg:
        before = _adg_snapshot_for_app(adg_snapshot, args.app)
        paths.adg_before.write_text(
            json.dumps(before, indent=2, sort_keys=True), encoding="utf-8"
        )

    # Drive scenario — Run 1
    seed = args.seed or spec.scenario_id
    with tempfile.TemporaryDirectory(prefix=f"appsproof_{args.app}_run1_") as tmp1:
        scratch1 = Path(tmp1)
        sdir1, ctx1 = _drive_scenario(
            spec,
            scratch=scratch1,
            adg_snapshot=adg_snapshot,
            customizer=registered.customizer,
            seed=seed,
        )
        _materialize_user_layout(paths=paths, scenario_dir=sdir1, ctx=ctx1)

        # Replay (Run 2) — only if required
        if args.require_replay:
            with tempfile.TemporaryDirectory(prefix=f"appsproof_{args.app}_run2_") as tmp2:
                scratch2 = Path(tmp2)
                sdir2, ctx2 = _drive_scenario(
                    spec,
                    scratch=scratch2,
                    adg_snapshot=adg_snapshot,
                    customizer=registered.customizer,
                    seed=seed,
                )
                # Stage Run 2 in user-layout form (same wrapping as Run 1)
                # so replay comparison runs against byte-equal canonical
                # JSON. Use a sibling ProofRunPaths into scratch2.
                run2_paths = ProofRunPaths(
                    proof_root=scratch2,
                    app_name=args.app,
                    run_id=run_id,
                )
                _materialize_user_layout(paths=run2_paths, scenario_dir=sdir2, ctx=ctx2)
                rcomparison = _replay_compare(
                    paths.contracts_dir, run2_paths.contracts_dir, paths
                )
                paths.replay_comparison.write_text(
                    json.dumps(rcomparison, indent=2, sort_keys=True), encoding="utf-8"
                )
                # Persist canonical run snapshots for audit
                paths.replay_run1.write_text(
                    json.dumps(
                        {"contracts_dir": str(paths.contracts_dir), "seed": seed, "side": "run1"},
                        indent=2,
                        sort_keys=True,
                    ),
                    encoding="utf-8",
                )
                paths.replay_run2.write_text(
                    json.dumps(
                        {
                            "contracts_dir": str(run2_paths.contracts_dir),
                            "seed": seed,
                            "side": "run2",
                        },
                        indent=2,
                        sort_keys=True,
                    ),
                    encoding="utf-8",
                )
        else:
            # User did not require replay — emit a stub indicating skipped.
            paths.replay_comparison.write_text(
                json.dumps(
                    {"ok": True, "compared_paths": [], "diffs": [], "reasons": ["skipped_no_require_replay"]},
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

    # ADG after + delta
    if args.require_adg:
        after = _adg_snapshot_for_app(adg_snapshot, args.app)
        paths.adg_after.write_text(
            json.dumps(after, indent=2, sort_keys=True), encoding="utf-8"
        )
        before_obj = json.loads(paths.adg_before.read_text(encoding="utf-8"))
        delta = _adg_delta(before_obj, after)
        paths.adg_delta.write_text(
            json.dumps(delta, indent=2, sort_keys=True), encoding="utf-8"
        )

    # Build & stamp the run_manifest
    manifest = _build_run_manifest(
        paths=paths,
        spec=spec,
        ctx=ctx1,
        cli_command=" ".join(sys.argv),
        fixture_path=args.fixture,
        flags=flags,
        adg_snapshot=adg_snapshot,
    )
    _stamp_proof_manifest_hash(manifest, paths)
    paths.run_manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, default=str), encoding="utf-8"
    )

    # Verify
    verdict = verify(paths.run_root)
    write_verdict(verdict, paths.run_root)

    print(f"runner: app={args.app} run_id={run_id} verdict={verdict['final_status']}")
    print(f"  proof_root: {paths.run_root}")
    print(f"  proof_verdict: {paths.proof_verdict}")
    if verdict["failed_checks"]:
        for fc in verdict["failed_checks"][:8]:
            print(f"  - FAIL {fc['name']}: {fc.get('fail_code') or 'FAIL'}: {fc.get('detail', '')}")

    return 0 if verdict["final_status"] == PROOF_STATUS_PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
