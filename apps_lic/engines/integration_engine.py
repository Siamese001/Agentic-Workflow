"""HOP9 integration — assemble fields for the final run record.

Emits ``lic_run_record_fields`` — a dict for L2/Exit receipt assembly (canonical spine)
reads when building the terminal ``GovernedLicE2ERunRecord``. Keeping
the record-assembly logic here (instead of inside the orchestrator)
isolates the final-shape concern from the walk plumbing.
"""

from __future__ import annotations

from typing import Any


class IntegrationEngine:
    """Collate terminal fields from upstream stage outputs."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        req = context.get("campaign_request")
        draft = context.get("draft_message") or {}
        report = context.get("validation_report") or {}
        qa = context.get("qa_report") or {}
        reasoning_policy = context.get("reasoning_policy") or draft.get("reasoning_policy") or {}

        config = self._attr(req, "config", None)

        return {
            "lic_run_record_fields": {
                "campaign_id": str(self._attr(req, "campaign_id", "")),
                "target_audience": str(self._attr(config, "target_audience", "")),
                "compliance_level": str(self._attr(config, "compliance_level", "standard")),
                "draft_body": str(draft.get("message_text") or draft.get("body", "")),
                "channel": str(draft.get("channel", "linkedin")),
                "recipient_class": str(draft.get("recipient_class", "recruiter")),
                "validation_passed": bool(report.get("passed", False)),
                "composite_score": float(qa.get("composite_score", 0.0)),
                "issues": list(report.get("issues") or []),
                "generator": str(draft.get("generator", "unknown")),
                "provider_profile": str(draft.get("provider_profile", "")),
                "model": str(draft.get("model", "")),
                "reasoning_policy": dict(reasoning_policy)
                if isinstance(reasoning_policy, dict)
                else {},
                "sc_level": str(
                    draft.get("sc_level")
                    or qa.get("sc_level")
                    or self._attr(reasoning_policy, "sc_level", "")
                ),
                "reasoning_intensity": str(
                    draft.get("reasoning_intensity")
                    or qa.get("reasoning_intensity")
                    or self._attr(reasoning_policy, "reasoning_intensity", "")
                ),
                "judge_profile": str(
                    draft.get("judge_profile")
                    or qa.get("judge_profile")
                    or self._attr(reasoning_policy, "judge_profile", "")
                ),
                "active_judges": list(qa.get("active_judges") or []),
                "x2_deterministic_gates": list(qa.get("x2_deterministic_gates") or []),
                "x1d_llm_judges": list(qa.get("x1d_llm_judges") or []),
                "x1d_model_backed_pass": bool(qa.get("x1d_model_backed_pass", False)),
            },
        }

    @staticmethod
    def _attr(obj: Any, key: str, default: Any) -> Any:
        if obj is None:
            return default
        if hasattr(obj, key):
            return getattr(obj, key, default)
        if isinstance(obj, dict):
            return obj.get(key, default)
        return default
