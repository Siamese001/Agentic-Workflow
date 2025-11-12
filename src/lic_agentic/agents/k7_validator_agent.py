"""Validator agent for outreach drafts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Tuple

from ..qa import MetricsTracker, QAResult, QAValidator

RetryFn = Callable[[QAResult, str, Dict[str, str]], Tuple[str, Dict[str, str]] | None]


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    reasons: Tuple[str, ...]
    final_draft: str

    @property
    def ok(self) -> bool:  # pragma: no cover - compatibility helper
        return self.passed


class ValidatorAgent:
    """Run QA validation with optional reflexive retries."""

    def __init__(
        self,
        qa_validator: QAValidator | None = None,
        metrics: MetricsTracker | None = None,
        *,
        max_retries: int = 1,
    ) -> None:
        self.qa_validator = qa_validator or QAValidator()
        self.metrics = metrics or MetricsTracker()
        self.max_retries = max(0, max_retries)

    def check(
        self,
        draft: str,
        route_decision,
        pii_map: Dict[str, str],
        *,
        artifacts: Dict[str, str] | None = None,
        retry_fn: RetryFn | None = None,
        token_count: int | None = None,
        latency_ms: int | None = None,
    ) -> ValidationResult:
        artifacts = dict(artifacts or {})
        placeholders: Iterable[str] = tuple(pii_map.keys()) if pii_map else ()

        current_draft = draft
        current_artifacts = artifacts
        qa_result = self.qa_validator.validate(
            current_draft, current_artifacts, pii_placeholders=placeholders
        )
        attempts = 0
        initial_tokens = token_count if token_count is not None else len(draft.split())
        while not qa_result.ok and attempts < self.max_retries:
            attempts += 1
            candidate = (
                retry_fn(qa_result, current_draft, current_artifacts)
                if retry_fn
                else self._default_retry(qa_result, current_draft, current_artifacts)
            )
            if not candidate:
                break
            current_draft, current_artifacts = candidate
            qa_result = self.qa_validator.validate(
                current_draft, current_artifacts, pii_placeholders=placeholders
            )

        final_tokens = len(current_draft.split())
        baseline_tokens = initial_tokens if initial_tokens else final_tokens
        drift = 0.0
        if baseline_tokens:
            drift = abs(final_tokens - baseline_tokens) / max(baseline_tokens, 1)

        self.metrics.record(
            qa_result,
            latency_ms=latency_ms,
            token_count=final_tokens,
            retry_attempted=attempts > 0,
            retry_succeeded=attempts > 0 and qa_result.ok,
            token_drift=drift,
        )
        return ValidationResult(qa_result.ok, qa_result.reasons, current_draft)

    def _default_retry(
        self, qa_result: QAResult, draft: str, artifacts: Dict[str, str]
    ) -> Tuple[str, Dict[str, str]] | None:
        lines = draft.splitlines()
        changed = False

        if "cta" in qa_result.missing_sections:
            signature_index = self._locate_signature_line(lines)
            cta_line = "CTA: Would you be open to a quick chat next week?"
            if signature_index is not None:
                if signature_index > 0 and lines[signature_index - 1].strip():
                    lines.insert(signature_index, "")
                    signature_index += 1
                lines.insert(signature_index, cta_line)
            else:
                if lines and lines[-1].strip():
                    lines.append("")
                lines.append(cta_line)
            changed = True

        if "signature" in qa_result.missing_sections:
            if lines and lines[-1].strip():
                lines.append("")
            lines.extend(["Best regards,", "LIC Outreach Bot"])
            changed = True

        if "value_wedge" in qa_result.missing_sections and artifacts:
            artifact_id, summary = next(iter(artifacts.items()))
            marker = f"[artifact_id:{artifact_id}] {summary}"
            if marker not in lines:
                insertion_index = self._first_body_index(lines)
                if insertion_index is None:
                    insertion_index = len(lines)
                else:
                    insertion_index += 1
                lines.insert(insertion_index, marker)
                changed = True

        for artifact_id in qa_result.missing_artifacts:
            if artifact_id in artifacts:
                marker_line = f"[artifact_id:{artifact_id}] {artifacts[artifact_id]}"
                if marker_line not in lines:
                    insertion_index = self._first_body_index(lines) or len(lines)
                    lines.insert(insertion_index + 1, marker_line)
                    changed = True

        if not changed:
            return None

        new_draft = "\n".join(lines)
        return new_draft, artifacts

    @staticmethod
    def _locate_signature_line(lines: List[str]) -> int | None:
        for index in range(len(lines) - 1, -1, -1):
            lowered = lines[index].lower()
            if any(keyword in lowered for keyword in QAValidator._SIGNATURE_KEYWORDS):
                return index
        return None

    @staticmethod
    def _first_body_index(lines: List[str]) -> int | None:
        for index in range(1, len(lines)):
            if lines[index].strip():
                return index
        return None
