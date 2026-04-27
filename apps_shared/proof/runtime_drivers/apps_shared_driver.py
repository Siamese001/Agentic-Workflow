"""apps_shared substrate driver — meta proof, no verticalization.

Per user spec §"apps_shared":
    "Treat as shared governed substrate. Do NOT add fake business data.
     Shared code must support trace, replay, provenance, contracts, and
     gates for app runs."

The driver verifies that the substrate modules required by every per-app
proof scenario are importable and expose their canonical contract classes.
It does NOT instantiate any business engine — apps_shared is infrastructure.
"""

from __future__ import annotations

import importlib
from pathlib import Path

from apps_shared.proof.runtime_drivers._driver_base import (
    write_artifact,
)


class AppsSharedDriver:
    app_id = "apps_shared"

    def invoke(self, ctx) -> dict[str, str]:
        fixture = dict(ctx.spec.extra_payload or {})

        expected_modules = list(fixture.get("expected_modules") or [])
        expected_contract_classes = list(fixture.get("expected_contract_classes") or [])

        # 1. Runtime spine report — every expected module must import
        spine_results = []
        for mod_path in expected_modules:
            try:
                importlib.import_module(mod_path)
                spine_results.append({"module": mod_path, "ok": True, "detail": "imported"})
            except ImportError as exc:
                spine_results.append({"module": mod_path, "ok": False, "detail": f"ImportError: {exc!r}"})
            except (RuntimeError, ValueError, TypeError, AttributeError) as exc:
                spine_results.append({"module": mod_path, "ok": False, "detail": f"InitError: {exc!r}"})
        runtime_spine_report = {
            "substrate_id": fixture.get("substrate_id"),
            "expected_count": len(expected_modules),
            "ok_count": sum(1 for r in spine_results if r["ok"]),
            "results": spine_results,
        }

        # 2. Contract schema report — every expected class is in proof_contracts
        try:
            pc = importlib.import_module("apps_shared.proof.proof_contracts")
            class_results = []
            for klass in expected_contract_classes:
                ok = hasattr(pc, klass)
                class_results.append({"class": klass, "present": ok})
            contract_schema_report = {
                "substrate_id": fixture.get("substrate_id"),
                "module": "apps_shared.proof.proof_contracts",
                "results": class_results,
                "all_present": all(r["present"] for r in class_results),
            }
        except ImportError as exc:
            contract_schema_report = {
                "substrate_id": fixture.get("substrate_id"),
                "error": f"ImportError: {exc!r}",
                "results": [],
                "all_present": False,
            }

        # 3. Trace helpers report — confirms scenario_base + otel_export
        trace_helpers_results = []
        for mod_path in (
            "apps_shared.proof.scenario_base",
            "apps_shared.proof.otel_export",
        ):
            try:
                m = importlib.import_module(mod_path)
                exports = [n for n in dir(m) if not n.startswith("_")]
                trace_helpers_results.append({
                    "module": mod_path,
                    "ok": True,
                    "public_export_count": len(exports),
                })
            except ImportError as exc:
                trace_helpers_results.append({
                    "module": mod_path, "ok": False, "detail": f"ImportError: {exc!r}",
                })
        trace_helpers_report = {
            "substrate_id": fixture.get("substrate_id"),
            "results": trace_helpers_results,
            "all_present": all(r.get("ok", False) for r in trace_helpers_results),
        }

        # 4. Replay helpers report — confirms validators._strip_volatile + run_app_scenario
        replay_helpers_results = []
        try:
            v = importlib.import_module("apps_shared.proof.validators")
            replay_helpers_results.append({
                "symbol": "apps_shared.proof.validators._strip_volatile",
                "present": hasattr(v, "_strip_volatile"),
            })
            replay_helpers_results.append({
                "symbol": "apps_shared.proof.validators.validate_replay",
                "present": hasattr(v, "validate_replay"),
            })
        except ImportError as exc:
            replay_helpers_results.append({
                "symbol": "apps_shared.proof.validators",
                "present": False,
                "detail": f"ImportError: {exc!r}",
            })
        try:
            sb = importlib.import_module("apps_shared.proof.scenario_base")
            replay_helpers_results.append({
                "symbol": "apps_shared.proof.scenario_base.run_app_scenario",
                "present": hasattr(sb, "run_app_scenario"),
            })
        except ImportError as exc:
            replay_helpers_results.append({
                "symbol": "apps_shared.proof.scenario_base",
                "present": False,
                "detail": f"ImportError: {exc!r}",
            })
        replay_helpers_report = {
            "substrate_id": fixture.get("substrate_id"),
            "results": replay_helpers_results,
            "all_present": all(r.get("present", False) for r in replay_helpers_results),
        }

        outputs: dict[str, str] = {}
        k, p = write_artifact(ctx, rel_filename="shared_runtime_spine_report.json", payload=runtime_spine_report, kind="SharedRuntimeSpineReport")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="shared_contract_schema_report.json", payload=contract_schema_report, kind="SharedContractSchemaReport")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="shared_trace_helpers_report.json", payload=trace_helpers_report, kind="SharedTraceHelpersReport")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="shared_replay_helpers_report.json", payload=replay_helpers_report, kind="SharedReplayHelpersReport")
        outputs[k] = p
        return outputs
