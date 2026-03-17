# MERGED FROM UNASSIGNED BY WINDSURF v4 — 2025-12-07T01:21:36.310145+00:00
# Original location: 10_tests\_unassigned_tests_invalid\test_rg_contact_research_executor.py
# High-signal content preserved below — zero-loss migration
# ================================================================================

"""
L2 safety execution for resume compliance and protection workflows.

Executes comprehensive safety validation to ensure resume content
meets security standards for job alignment.
"""

from __future__ import annotations

# from archives.legacy_root_folders.runtime.runtime_utils import invoke_model, SandboxConfig  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.core.routing import RoutingPolicy  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.core.models.models import ComplexityLevel  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_resume_gen.Agentic_Workflow-10_10.config.meta_profile import MetaProfileSnapshot  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_resume_gen.Agentic_Workflow-10_10.tests.sandbox.test_sandbox_observability import record_event, record_exception  # DEPRECATED: Archive import removed to protect archives from validation edits


class SafetyExecutor:
    """
    Executes resume safety validation with optimal model selection.

    Protects user data and ensures compliance for reliable resume
    processing workflows and job alignment.
    """

    def __init__(
        self,
        routing_policy: RoutingPolicy,
        sandbox: SandboxConfig,
        meta_profile: MetaProfileSnapshot | None = None,
    ):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile

    def execute_safety(self, prompt: str) -> str:
        """
        Executes resume safety validation using LLM models.

        Ensures content compliance and protection for secure resume
        improvement processes and job alignment.
        """
        try:
            model = self.routing_policy.select_model(
                Task="safety_execution",
                complexity=ComplexityLevel.MEDIUM,
                meta_profile=self.meta_profile,
            )

            record_event("safety_execution_start", {"Task": "safety_execution"})

            result = invoke_model(
                model=model,
                prompt=prompt,
                sandbox=self.sandbox,
            )

            record_event("safety_execution_success", {"result_length": len(result)})
            return result

        except (ValueError, TypeError, RuntimeError, KeyError) as exc:
            record_exception("safety_execution_failure", exc)
            raise
