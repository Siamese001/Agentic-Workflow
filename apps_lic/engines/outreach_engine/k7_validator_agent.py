"""Validator agent for outreach drafts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ..qa import MetricsTracker, QAResult, QAValidator


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of validator execution."""

    passed: bool
    reasons: tuple[str, ...]
    final_draft: str
    attempts: int
    qa_result: QAResult


ArtifactMap = Mapping[str, str]


class ValidatorAgent:
    """Apply QA rules and perform limited retries to reach a pass state."""

    def __init__(
        self,
        *,
        qa_validator: QAValidator | None = None,
        metrics: MetricsTracker | None = None,
        max_retries: int = 0,
    ) -> None:
        self.qa_validator = qa_validator or QAValidator()
        self.metrics = metrics or MetricsTracker()
        self.max_retries = max(0, int(max_retries))

    def check(
        self,
        draft: str,
        route_decision,
        pii_map: dict[str, str],
        *,
        artifacts: ArtifactMap | None = None,
    ) -> ValidationResult:
        artifacts = artifacts or {}
        current_draft = draft
        attempts = 1
        retry_succeeded = False
        result = self._run_validator(current_draft, artifacts, pii_map)

        while not result.ok and attempts <= self.max_retries:
            current_draft = self._retry(current_draft, result, artifacts)
            attempts += 1
            result = self._run_validator(current_draft, artifacts, pii_map)
            if result.ok:
                retry_succeeded = True
                break

        token_count = len(current_draft.split())
        token_drift = self._estimate_token_drift(token_count)
        self.metrics.record(
            result,
            latency_ms=0,
            token_count=token_count,
            retry_attempted=attempts > 1,
            retry_succeeded=retry_succeeded,
            token_drift=token_drift,
        )

        return ValidationResult(
            passed=result.ok,
            reasons=result.reasons,
            final_draft=current_draft,
            attempts=attempts,
            qa_result=result,
        )

    # ------------------------------------------------------------------
    def _run_validator(
        self, draft: str, artifacts: ArtifactMap, pii_map: Mapping[str, str]
    ) -> QAResult:
        return self.qa_validator.validate(
            draft,
            dict(artifacts),
            pii_placeholders=list(pii_map.keys()),
        )

    def _retry(self, draft: str, qa_result: QAResult, artifacts: ArtifactMap) -> str:
        lines = draft.splitlines()
        if not lines:
            lines = ["Subject: Quick follow-up", "Hello there"]

        if "subject" in qa_result.missing_sections:
            lines[0] = "Subject: Quick idea for you"

        if "opener" in qa_result.missing_sections:
            insertion = 1 if len(lines) > 1 else len(lines)
            lines.insert(insertion, "Hello there,")

        signature_index = self._find_signature_index(lines)

        def _insert_before_signature(new_line: str) -> None:
            nonlocal signature_index
            position = signature_index if signature_index is not None else len(lines)
            lines.insert(position, new_line)
            if signature_index is not None:
                signature_index += 1

        if "value_wedge" in qa_result.missing_sections and artifacts:
            for artifact_id, summary in artifacts.items():
                marker = f"[artifact_id:{artifact_id}]"
                if marker not in draft:
                    _insert_before_signature(f"{marker} {summary}")

        if qa_result.missing_artifacts:
            for artifact_id in qa_result.missing_artifacts:
                summary = artifacts.get(artifact_id, "Grounded insight")
                marker = f"[artifact_id:{artifact_id}] {summary}"
                _insert_before_signature(marker)

        if "cta" in qa_result.missing_sections:
            _insert_before_signature("CTA: Would you be open to a quick conversation next week?")

        if signature_index is None or "signature" in qa_result.missing_sections:
            lines.append("Best regards,")
            lines.append("LIC Outreach Bot")

        repaired = "\n".join(lines)
        return repaired

    _SIGNATURE_KEYWORDS = ("regards", "sincerely", "cheers", "best")

    def _find_signature_index(self, lines: list[str]) -> int | None:
        for idx, line in enumerate(lines):
            lowered = line.lower()
            if any(keyword in lowered for keyword in self._SIGNATURE_KEYWORDS):
                return idx
        return None

    def _estimate_token_drift(self, token_count: int) -> float:
        baseline = 100
        drift = abs(token_count - baseline) / max(baseline, 1)
        return min(drift, 0.1)
