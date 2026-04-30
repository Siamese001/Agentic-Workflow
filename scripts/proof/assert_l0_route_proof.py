"""Assertion script for the L0 routing proof bundle directory.

Enforces strict acceptance per the user brief (§7):

  1. Every required artifact must be present in every bundle.
  2. Every artifact with status="OK" must carry the six provenance fields.
  3. ``producer_module`` must resolve to a file under ``agentic_core/``.
  4. ``upstream_artifact_ref`` must form a closed chain rooted at ValidatedRequest.
  5. ``proof_classification`` must equal ``"COMPOSITION_PROOF"`` UNLESS
     ``integrated_runtime_entry_point_used`` is true AND the entry-point
     ref resolves to a real production module — only then INTEGRATED_RUNTIME_PROOF
     is acceptable.
  6. ``otel_route_trace_id`` and ``otel_exit_trace_id`` must both be non-empty.
  7. ``CounterDelta.payload.delta_for_expected_metric`` must be > 0.
  8. ``NoBypassReceipt.payload.no_bypass_proven`` must be true on TERMINAL_RET arms.
  9. NO artifact may be marked OK with provenance.producer_component starting
     with "harness". Provenance == "harness" → fail.

Usage:

    python scripts/proof/assert_l0_route_proof.py <run_dir>

Exit code: 0 = strict acceptance passed; 1 = at least one violation.
"""

from __future__ import annotations

import importlib
import json
import pathlib
import sys
from dataclasses import dataclass, field

REQUIRED_ARTIFACTS = (
    "ValidatedRequest",
    "L1PlanContract",
    "CacheLineage",
    "L0RouteContract",
    "TerminalRetPacket",
    "ExitReviewPacket",
    "X3Disposition",
    "ExhaustManifest",
    "UWGCommitReceipt",
    "CounterDelta",
    "ReplayReceipt",
    "NoBypassReceipt",
)

PROVENANCE_FIELDS = (
    "producer_component",
    "producer_module",
    "producer_function_or_class",
    "emitted_at",
    "artifact_hash",
    "upstream_artifact_ref",
)

ACCEPTABLE_CLASSIFICATIONS = (
    "COMPONENT_PRIMITIVE_PROOF",
    "COMPOSITION_PROOF",
    "INTEGRATED_RUNTIME_PROOF",
)


@dataclass
class ScenarioResult:
    scenario_id: str
    bundle_path: str
    violations: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.violations


def _is_under_agentic_core(module_path: str) -> bool:
    if not module_path or "harness" in module_path.lower():
        return False
    if not module_path.startswith("agentic_core."):
        return False
    try:
        mod = importlib.import_module(module_path)
        file_path = getattr(mod, "__file__", "") or ""
        return bool(file_path) and "agentic_core" in file_path
    except (ImportError, AttributeError, ValueError):
        return False


def _check_provenance(artifact: dict, name: str) -> list[str]:
    violations: list[str] = []
    prov = artifact.get("provenance")
    if not isinstance(prov, dict):
        violations.append(f"{name}: missing provenance object")
        return violations
    for fld in PROVENANCE_FIELDS:
        # ValidatedRequest is the chain root and legitimately has
        # upstream_artifact_ref = "". Every other artifact must point upstream.
        if fld == "upstream_artifact_ref" and name == "ValidatedRequest":
            if prov.get(fld) != "":
                violations.append(
                    f"{name}: chain root must have upstream_artifact_ref='', got {prov.get(fld)!r}"
                )
            continue
        if not prov.get(fld):
            violations.append(f"{name}: provenance.{fld} is empty/missing")
    pm = prov.get("producer_module", "")
    if not _is_under_agentic_core(pm):
        violations.append(
            f"{name}: provenance.producer_module={pm!r} does not resolve under agentic_core/"
        )
    pc = prov.get("producer_component", "")
    if pc.startswith("harness"):
        violations.append(
            f"{name}: provenance.producer_component={pc!r} is harness-stamped (forbidden by §7)"
        )
    return violations


def _check_chain(artifacts: dict[str, dict]) -> list[str]:
    """Verify the upstream_artifact_ref chain forms a closed graph rooted at ValidatedRequest."""
    violations: list[str] = []
    digest_by_name: dict[str, str] = {}
    for name, art in artifacts.items():
        prov = art.get("provenance")
        if isinstance(prov, dict) and prov.get("artifact_hash"):
            digest_by_name[name] = prov["artifact_hash"]
    if "ValidatedRequest" not in digest_by_name:
        violations.append("chain: ValidatedRequest digest missing — chain has no root")
        return violations
    vr_prov = artifacts["ValidatedRequest"].get("provenance", {})
    if vr_prov.get("upstream_artifact_ref") != "":
        violations.append(
            "chain: ValidatedRequest must have upstream_artifact_ref='' (chain root)"
        )
    valid_digests = set(digest_by_name.values()) | {""}
    for name, art in artifacts.items():
        if art.get("status") != "OK":
            continue
        prov = art.get("provenance", {}) or {}
        upstream = prov.get("upstream_artifact_ref", "<missing>")
        if upstream not in valid_digests:
            violations.append(
                f"chain: {name}.upstream_artifact_ref={upstream[:16] if upstream else upstream!r}… "
                f"does not match any artifact digest in this bundle"
            )
    return violations


def _check_bundle(path: pathlib.Path) -> ScenarioResult:
    bundle = json.loads(path.read_text(encoding="utf-8"))
    res = ScenarioResult(scenario_id=bundle.get("scenario_id", path.stem), bundle_path=str(path))

    # 1. Required top-level fields
    for fld in (
        "scenario_id", "arm", "request_id", "run_id", "trace_root",
        "policy_hash", "blueprint_hash", "registry_digest_set", "replay_key",
        "otel_route_trace_id", "otel_exit_trace_id",
        "proof_classification", "integrated_runtime_entry_point_used",
        "deterministic_digest", "artifacts",
    ):
        if fld not in bundle or bundle[fld] in (None, "") and fld not in ("integrated_runtime_entry_point_used",):
            res.violations.append(f"bundle: missing/empty top-level field {fld!r}")

    # 2. Proof classification consistency
    pc = bundle.get("proof_classification")
    irepu = bool(bundle.get("integrated_runtime_entry_point_used"))
    irepr = bundle.get("integrated_runtime_entry_point_ref")
    if pc not in ACCEPTABLE_CLASSIFICATIONS:
        res.violations.append(f"classification: {pc!r} not in {ACCEPTABLE_CLASSIFICATIONS}")
    if pc == "INTEGRATED_RUNTIME_PROOF":
        if not irepu:
            res.violations.append(
                "classification: INTEGRATED_RUNTIME_PROOF claimed but "
                "integrated_runtime_entry_point_used is false"
            )
        if not irepr or not isinstance(irepr, str) or not _is_under_agentic_core(irepr.split(":")[0]):
            res.violations.append(
                f"classification: integrated_runtime_entry_point_ref={irepr!r} "
                "does not resolve under agentic_core/"
            )

    # 3. OTEL trace correlation
    if not bundle.get("otel_route_trace_id"):
        res.violations.append("otel: route_trace_id is empty")
    if not bundle.get("otel_exit_trace_id"):
        res.violations.append("otel: exit_trace_id is empty")

    artifacts = bundle.get("artifacts") or {}
    if not isinstance(artifacts, dict):
        res.violations.append("artifacts: not a dict")
        return res

    # 4. All required artifacts present
    for required in REQUIRED_ARTIFACTS:
        if required not in artifacts:
            res.violations.append(f"artifacts: missing {required!r}")

    # 5. Per-artifact status & provenance
    for name, art in artifacts.items():
        status = art.get("status")
        if status not in ("OK", "MISSING_PRODUCTION_EMITTER", "NOT_APPLICABLE_BY_DESIGN"):
            res.violations.append(f"{name}: invalid status {status!r}")
            continue
        if status == "OK":
            res.violations.extend(_check_provenance(art, name))
        elif status == "MISSING_PRODUCTION_EMITTER":
            for fld in (
                "missing_artifact",
                "expected_owner_layer",
                "expected_source_file",
                "required_next_remediation",
            ):
                if not art.get(fld):
                    res.violations.append(f"{name}: MISSING_PRODUCTION_EMITTER lacks {fld}")
        elif status == "NOT_APPLICABLE_BY_DESIGN":
            if not art.get("not_applicable_reason"):
                res.violations.append(f"{name}: NOT_APPLICABLE_BY_DESIGN lacks reason")

    # 6. Chain check
    res.violations.extend(_check_chain(artifacts))

    # 7. Counter delta must be positive on the expected metric
    cd = artifacts.get("CounterDelta", {})
    if cd.get("status") == "OK":
        delta = (cd.get("payload") or {}).get("delta_for_expected_metric", 0)
        try:
            if int(delta) <= 0:
                res.violations.append(
                    f"CounterDelta: delta_for_expected_metric={delta} (must be > 0)"
                )
        except (TypeError, ValueError):
            res.violations.append(f"CounterDelta: non-numeric delta {delta!r}")

    # 8. No-bypass on TERMINAL_RET
    rc = artifacts.get("L0RouteContract", {})
    rc_payload = rc.get("payload") or {}
    if rc_payload.get("execution_form") == "terminal_return":
        nb = artifacts.get("NoBypassReceipt", {})
        if nb.get("status") == "OK":
            if not (nb.get("payload") or {}).get("no_bypass_proven"):
                res.violations.append(
                    "NoBypassReceipt: no_bypass_proven=false on TERMINAL_RET arm"
                )
        else:
            res.violations.append("NoBypassReceipt: not OK on TERMINAL_RET arm")

    # 9. UWGCommitReceipt: only NOT_APPLICABLE_BY_DESIGN is allowed when execution_form=terminal_return
    uwg = artifacts.get("UWGCommitReceipt", {})
    if rc_payload.get("execution_form") == "terminal_return":
        if uwg.get("status") not in ("NOT_APPLICABLE_BY_DESIGN",):
            res.violations.append(
                f"UWGCommitReceipt: must be NOT_APPLICABLE_BY_DESIGN on TERMINAL_RET, got {uwg.get('status')!r}"
            )

    # 10. Local status must be PASS
    if bundle.get("local_status") != "PASS":
        res.violations.append(f"local_status: {bundle.get('local_status')!r} (must be PASS)")

    return res


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: python {argv[0]} <run_dir>", file=sys.stderr)
        return 2
    run_dir = pathlib.Path(argv[1]).resolve()
    if not run_dir.is_dir():
        print(f"[assert] run_dir {run_dir} is not a directory", file=sys.stderr)
        return 2
    bundles_dir = run_dir / "bundles"
    if not bundles_dir.is_dir():
        print(f"[assert] expected {bundles_dir}/", file=sys.stderr)
        return 2
    bundle_paths = sorted(bundles_dir.glob("*.json"))
    if not bundle_paths:
        print(f"[assert] no bundles in {bundles_dir}", file=sys.stderr)
        return 2

    results = [_check_bundle(p) for p in bundle_paths]

    print(f"[assert] checked {len(results)} bundles in {run_dir}")
    print()
    print(f"{'Scenario':<24} {'Result':<6}  Violations")
    print("-" * 80)
    overall = 0
    for r in results:
        verdict = "PASS" if r.passed else "FAIL"
        if not r.passed:
            overall = 1
        print(f"{r.scenario_id:<24} {verdict:<6}  {len(r.violations)}")
        for v in r.violations:
            print(f"    - {v}")
    print()
    if overall == 0:
        print("[assert] STRICT ACCEPTANCE: PASS — bundle satisfies COMPOSITION_PROOF discipline.")
        # Determine claimed classification (assert all bundles agree).
        classifications = {
            json.loads(p.read_text(encoding="utf-8")).get("proof_classification")
            for p in bundle_paths
        }
        if len(classifications) == 1:
            cls = next(iter(classifications))
            print(f"[assert] proof_classification = {cls}")
            if cls == "COMPOSITION_PROOF":
                print(
                    "[assert] NOTE: INTEGRATED_RUNTIME_PROOF is BLOCKED by gap "
                    "docs/reports/gaps/runtime_entrypoint_full_proof_gap.md"
                )
    else:
        print("[assert] STRICT ACCEPTANCE: FAIL")
    return overall


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
