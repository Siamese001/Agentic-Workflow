"""L2 step adapters for apps_rg deterministic resume-generation recipe.

Each step is a callable class with ``__call__(context) -> dict`` interface.
Steps are **app-specific implementations only** — they must not:
  - decide route (L0 owns that)
  - emit X3 (Exit V6 owns that)
  - write L4 (UWG owns that)
  - bypass Prompt Assembly for model calls
  - silently call external research

These classes are imported by ``agentic_core.runtime.l2_recipe_resolver``
and chained into the L2 execution sequence.  They are NEVER called directly
by ``apps_rg.__main__``.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

_log = logging.getLogger("apps_rg.l2_recipe.steps")


class _PAGuard:
    """Fail-closed guard: LLM-backed steps must have a CompiledPromptArtifact.

    If the context already carries a compiled artifact (``compiled_prompt_artifact``),
    validation passes.  Otherwise, if enough governed context exists (JD, resume,
    flow_route), the guard compiles the artifact via the apps_rg PA compiler.
    If compilation fails, the step fails closed — no model call.
    """

    @staticmethod
    def check(context: dict[str, Any], step_name: str) -> dict[str, Any]:
        """Ensure context has a compiled prompt artifact.

        Returns the compiled artifact dict (or the pre-existing one).

        Raises:
            RuntimeError: PA_GUARD_FAILED or PA_COMPILE_FAILED if no artifact
                can be produced.
        """
        # Path 1: artifact already compiled (e.g., by upstream step or test)
        existing = context.get("compiled_prompt_artifact")
        if existing:
            from apps_rg.prompt_assembly.contracts import PACompileStatus
            status = existing.get("compile_status", "") if isinstance(existing, dict) else getattr(existing, "compile_status", "")
            if status == PACompileStatus.PA_L2_HANDOFF_READY.value:
                return existing if isinstance(existing, dict) else existing.to_dict()

        # Path 2: compile from governed context
        jd_data = context.get("jd_data", "")
        resume_data = context.get("master_resume_data", "")
        flow_route = context.get("flow_route", "")

        if not jd_data or not resume_data or not flow_route:
            raise RuntimeError(
                f"PA_GUARD_FAILED: {step_name} requires CompiledPromptArtifact "
                f"or governed context (jd_data + master_resume_data + flow_route) "
                f"to compile one. Missing: "
                f"{'jd_data ' if not jd_data else ''}"
                f"{'master_resume_data ' if not resume_data else ''}"
                f"{'flow_route' if not flow_route else ''}"
            )

        try:
            from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
            from apps_rg.prompt_assembly.compiler import compile_prompt

            request = AppsRgPromptRequest(
                flow_route=flow_route,
                jd_data=jd_data,
                master_resume_data=resume_data,
                company_brief_data=context.get("company_brief_data", ""),
                user_task=context.get("user_task", ""),
                claim_source_refs=context.get("claim_source_refs", ""),
                unsupported_claims=context.get("unsupported_claims", ""),
                approved_resume_examples=context.get("approved_resume_examples", ""),
                seniority_band=context.get("seniority_band", ""),
                target_company=context.get("target_company", ""),
                target_role=context.get("target_role", ""),
                local_evidence_contract_ref=context.get("local_evidence_contract_ref", ""),
                run_id=context.get("run_id", ""),
                trace_id=context.get("trace_id", ""),
                request_id=context.get("request_id", ""),
                provider_lane=context.get("provider_lane", "default"),
                symbolic_model_id=context.get("symbolic_model_id", ""),
                policy_hash=context.get("policy_hash", ""),
                blueprint_hash=context.get("blueprint_hash", ""),
            )
            artifact = compile_prompt(request)
            artifact_dict = artifact.to_dict()
            context["compiled_prompt_artifact"] = artifact_dict
            return artifact_dict
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"PA_COMPILE_FAILED: {step_name} failed to compile prompt "
                f"artifact: {exc}"
            ) from exc


class GenerateResumeStep:
    """HOP-4: Run generate_resume main pipeline (HOPs 1-3, K-nodes).

    Wraps ``apps_rg.scripts.generate_resume.main()`` as an L2 step adapter.
    This step contains LLM calls and therefore requires PA-compatible
    prompt artifacts.
    """

    STEP_ID = "hop_4_generate_resume"
    REQUIRES_PA = True

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        import asyncio
        from apps_rg.scripts.generate_resume import main as _generate

        artifact_dict = _PAGuard.check(context, self.STEP_ID)

        _log.info("[L2 step] %s: starting generate_resume (prompt_id=%s)",
                  self.STEP_ID, artifact_dict.get("prompt_id", "?"))
        asyncio.run(_generate())

        runs_root = Path("artifacts/apps_rg/runs")
        run_dir = None
        if runs_root.exists():
            candidates = sorted(
                (p for p in runs_root.iterdir() if p.is_dir()),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if candidates:
                run_dir = str(candidates[0])

        _log.info("[L2 step] %s: complete, run_dir=%s", self.STEP_ID, run_dir)
        return {
            "step_id": self.STEP_ID,
            "exit_code": 0,
            "run_dir": run_dir,
            "compiled_prompt_artifact": {
                "artifact_id": artifact_dict.get("artifact_id", ""),
                "prompt_id": artifact_dict.get("prompt_id", ""),
                "template_id": artifact_dict.get("template_id", ""),
                "template_version": artifact_dict.get("template_version", ""),
                "prompt_hash": artifact_dict.get("prompt_hash", ""),
                "prompt_template_hash": artifact_dict.get("prompt_template_hash", ""),
                "prompt_bom_hash": artifact_dict.get("prompt_bom_hash", ""),
                "prompt_registry_hash": artifact_dict.get("prompt_registry_hash", ""),
                "manifest_hash": artifact_dict.get("manifest_hash", ""),
                "canonical_slot_bytes_hash": artifact_dict.get("canonical_slot_bytes_hash", ""),
                "artifact_hash": artifact_dict.get("artifact_hash", ""),
                "replay_key": artifact_dict.get("replay_key", ""),
                "policy_hash": artifact_dict.get("policy_hash", ""),
                "blueprint_hash": artifact_dict.get("blueprint_hash", ""),
                "provider_lane": artifact_dict.get("provider_lane", ""),
                "compile_status": artifact_dict.get("compile_status", ""),
                "source_refs": artifact_dict.get("source_refs", {}),
                "origin_label_map": artifact_dict.get("origin_label_map", {}),
                "local_evidence_contract_ref": artifact_dict.get("local_evidence_contract_ref", ""),
                "output_schema_ref": artifact_dict.get("output_schema_ref", ""),
                "output_schema_hash": artifact_dict.get("output_schema_hash", ""),
            },
        }


class FactCheckStep:
    """E4_HEAL: Fact-check the generated resume against source data.

    Uses the ``resume_fact_check_v1`` governed template via PA compiler.
    """

    STEP_ID = "fact_check_generated_resume"
    REQUIRES_PA = True

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        from apps_rg.prompt_assembly.compiler import compile_prompt

        request = AppsRgPromptRequest(
            flow_route="fact_check",
            jd_data=context.get("jd_data", ""),
            master_resume_data=context.get("master_resume_data", ""),
            claim_source_refs=context.get("claim_source_refs", ""),
            run_id=context.get("run_id", ""),
            trace_id=context.get("trace_id", ""),
        )
        artifact = compile_prompt(request)
        artifact_dict = artifact.to_dict()
        _log.info("[L2 step] %s: compiled (prompt_id=%s)", self.STEP_ID, artifact.prompt_id)
        return {
            "step_id": self.STEP_ID,
            "exit_code": 0,
            "compiled_prompt_artifact": artifact_dict,
        }


class ClaimOmissionStep:
    """E4_HEAL: Omit unsupported claims from the generated resume.

    Uses the ``unsupported_claim_omission_v1`` governed template via PA compiler.
    """

    STEP_ID = "omit_unsupported_resume_claims"
    REQUIRES_PA = True

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        from apps_rg.prompt_assembly.compiler import compile_prompt

        request = AppsRgPromptRequest(
            flow_route="claim_omission",
            jd_data=context.get("jd_data", ""),
            master_resume_data=context.get("master_resume_data", ""),
            unsupported_claims=context.get("unsupported_claims", ""),
            run_id=context.get("run_id", ""),
            trace_id=context.get("trace_id", ""),
        )
        artifact = compile_prompt(request)
        artifact_dict = artifact.to_dict()
        _log.info("[L2 step] %s: compiled (prompt_id=%s)", self.STEP_ID, artifact.prompt_id)
        return {
            "step_id": self.STEP_ID,
            "exit_code": 0,
            "compiled_prompt_artifact": artifact_dict,
        }


class BulletDiversityRepairStep:
    """E4_HEAL: Repair bullet-point diversity in the generated resume.

    Uses the ``bullet_diversity_repair_v1`` governed template via PA compiler.
    """

    STEP_ID = "repair_bullet_diversity"
    REQUIRES_PA = True

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        from apps_rg.prompt_assembly.compiler import compile_prompt

        request = AppsRgPromptRequest(
            flow_route="bullet_diversity_repair",
            jd_data=context.get("jd_data", ""),
            master_resume_data=context.get("master_resume_data", ""),
            run_id=context.get("run_id", ""),
            trace_id=context.get("trace_id", ""),
        )
        artifact = compile_prompt(request)
        artifact_dict = artifact.to_dict()
        _log.info("[L2 step] %s: compiled (prompt_id=%s)", self.STEP_ID, artifact.prompt_id)
        return {
            "step_id": self.STEP_ID,
            "exit_code": 0,
            "compiled_prompt_artifact": artifact_dict,
        }


class DocxManifestStep:
    """E5_SEAL: Generate DOCX artifact manifest for the sealed output.

    Uses the ``docx_manifest_v1`` governed template via PA compiler.
    """

    STEP_ID = "docx_manifest_seal"
    REQUIRES_PA = True

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        from apps_rg.prompt_assembly.contracts import AppsRgPromptRequest
        from apps_rg.prompt_assembly.compiler import compile_prompt

        request = AppsRgPromptRequest(
            flow_route="docx_manifest",
            jd_data=context.get("jd_data", ""),
            master_resume_data=context.get("master_resume_data", ""),
            run_id=context.get("run_id", ""),
            trace_id=context.get("trace_id", ""),
        )
        artifact = compile_prompt(request)
        artifact_dict = artifact.to_dict()
        _log.info("[L2 step] %s: compiled (prompt_id=%s)", self.STEP_ID, artifact.prompt_id)
        return {
            "step_id": self.STEP_ID,
            "exit_code": 0,
            "compiled_prompt_artifact": artifact_dict,
        }


class NarrativePassStep:
    """HOP-5: Narrative Pass (HOPs 4A-4H, in-process subprocess).

    Wraps ``apps_rg.scripts.narrative_pass`` as an L2 step adapter.
    """

    STEP_ID = "hop_5_narrative_pass"
    REQUIRES_PA = False

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        run_dir = context.get("run_dir")
        target_company = context.get("target_company", "")
        target_role = context.get("target_role", "")

        if not target_company:
            _log.info("[L2 step] %s: skipped (no target_company)", self.STEP_ID)
            return {"step_id": self.STEP_ID, "exit_code": 0, "skipped": True}

        if not run_dir:
            _log.error("[L2 step] %s: no run_dir in context", self.STEP_ID)
            return {"step_id": self.STEP_ID, "exit_code": 1, "error": "no run_dir"}

        run_dir = Path(run_dir)
        input_resume = run_dir / "generated_resume.json"
        if not input_resume.exists():
            _log.error("[L2 step] %s: %s missing", self.STEP_ID, input_resume)
            return {"step_id": self.STEP_ID, "exit_code": 1, "error": "generated_resume.json missing"}

        cmd = [
            sys.executable, "-m", "apps_rg.scripts.narrative_pass",
            "--target-company", target_company,
            "--input-resume", str(input_resume),
            "--out-dir", str(run_dir),
            "--manual-brief", context.get("manual_brief", "apps_rg/scripts/company_research.json"),
        ]
        if context.get("research_via"):
            cmd.extend(["--research-via", context["research_via"]])
        if context.get("auto_research_internal"):
            cmd.append("--auto-research-internal")
        if context.get("auto_research_tavily"):
            cmd.append("--auto-research-tavily")
        if target_role:
            cmd.extend(["--target-role", target_role])

        _log.info("[L2 step] %s: starting narrative pass", self.STEP_ID)
        try:
            result = subprocess.run(cmd, timeout=600, shell=False)
        except subprocess.TimeoutExpired:
            _log.error("[L2 step] %s: narrative pass timed out", self.STEP_ID)
            return {"step_id": self.STEP_ID, "exit_code": 124, "error": "timeout"}

        _log.info("[L2 step] %s: exit_code=%s", self.STEP_ID, result.returncode)
        return {"step_id": self.STEP_ID, "exit_code": result.returncode}


class DocxExportStep:
    """HOP-6: DOCX Export (in-process subprocess).

    Wraps ``apps_rg.outputs.docx_exporter`` as an L2 step adapter.
    """

    STEP_ID = "hop_6_docx_export"
    REQUIRES_PA = False

    def __call__(self, context: dict[str, Any]) -> dict[str, Any]:
        run_dir = context.get("run_dir")
        target_company = context.get("target_company", "")
        target_role = context.get("target_role", "")

        if not run_dir:
            _log.error("[L2 step] %s: no run_dir in context", self.STEP_ID)
            return {"step_id": self.STEP_ID, "exit_code": 1, "error": "no run_dir"}

        cmd = [
            sys.executable, "-m", "apps_rg.outputs.docx_exporter",
            "--run-dir", str(run_dir),
        ]
        if target_role and target_company:
            cmd.extend(["--target-role", target_role, "--target-company", target_company])

        _log.info("[L2 step] %s: starting DOCX export", self.STEP_ID)
        try:
            result = subprocess.run(cmd, timeout=120, shell=False)
        except subprocess.TimeoutExpired:
            _log.error("[L2 step] %s: DOCX export timed out", self.STEP_ID)
            return {"step_id": self.STEP_ID, "exit_code": 124, "error": "timeout"}

        _log.info("[L2 step] %s: exit_code=%s", self.STEP_ID, result.returncode)
        return {"step_id": self.STEP_ID, "exit_code": result.returncode}
