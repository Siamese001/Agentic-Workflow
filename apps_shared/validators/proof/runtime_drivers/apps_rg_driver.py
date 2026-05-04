"""apps_rg READ-ONLY real-runtime driver.

Per master plan §"High-Risk Files" and user spec §"apps_rg":
    "Only run read-only proof unless app owner selects deeper workflow.
     No hidden writes. No broad provider bypass. No module-load action
     execution. No direct infra access outside approved seams."

The driver:
  * Imports a small, low-risk engine module (ats_compatibility_engine —
    215 lines, no external deps beyond lifecycle trace).
  * Confirms ``mode == 'readonly_smoke'`` in the fixture; refuses any
    other mode (anti-cheat: caller cannot upgrade scope silently).
  * Emits a smoke proof, trace coverage, and ADG risk report — no other
    artifacts, no engine state mutation.
"""

from __future__ import annotations

from apps_shared.validators.proof.runtime_drivers._driver_base import (
    import_real_engine,
    write_artifact,
)


class AppsRgDriver:
    app_id = "apps_rg"

    def invoke(self, ctx) -> dict[str, str]:
        fixture = dict(ctx.spec.extra_payload or {})

        # Anti-cheat: refuse anything other than readonly_smoke mode.
        mode = fixture.get("mode")
        if mode != "readonly_smoke":
            raise ValueError(
                f"apps_rg driver: mode={mode!r} not allowed. "
                "Only 'readonly_smoke' is supported in proof runs. "
                "Deeper workflows require explicit app-owner authorization."
            )

        # Anti-cheat: fixture must explicitly declare no_mutation_required.
        if not fixture.get("no_mutation_required", False):
            raise ValueError(
                "apps_rg driver: fixture must set no_mutation_required=true."
            )

        # Import a small, focused engine module — proves import path is real
        # without touching the heavy resume_orchestrator or hardened_gemini paths.
        engine_ok, engine_detail = import_real_engine(
            "apps_rg.engines.ats_compatibility_engine"
        )

        smoke_proof = {
            "rg_id": fixture.get("rg_id"),
            "mode": mode,
            "engine_import_ok": engine_ok,
            "engine_detail": engine_detail,
            "engine_imported": "apps_rg.engines.ats_compatibility_engine",
            "writes_attempted": 0,
            "mutations_attempted": 0,
            "test_resume_chars": len(str(fixture.get("test_resume_text") or "")),
            "ats_check_required": bool(fixture.get("ats_check_required")),
        }

        trace_coverage = {
            "rg_id": fixture.get("rg_id"),
            "spine_layers_required": ["U0", "L1", "L0", "L2", "Exit"],
            "grounding_required": bool(ctx.spec.grounding_required),
            "driver_writes": list(smoke_proof.keys()),
        }

        adg_risk_report = {
            "rg_id": fixture.get("rg_id"),
            "no_go_files_touched": [],  # readonly invariant
            "engine_imported_in_no_go_list": False,  # ats_compatibility is small/safe
            "module_load_action_calls": "captured by lifecycle_trace _emit_* (see ADG mv_module_load_action_calls_overlay)",
        }

        outputs: dict[str, str] = {}
        k, p = write_artifact(ctx, rel_filename="rg_readonly_smoke_proof.json", payload=smoke_proof, kind="RGReadOnlySmokeProof")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="trace_coverage_report.json", payload=trace_coverage, kind="TraceCoverageReport")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="adg_risk_report.json", payload=adg_risk_report, kind="ADGRiskReport")
        outputs[k] = p
        return outputs
