"""C0 Evidence Airlock — isolates retrieved content with provenance.

Ensures verified evidence (JD, master résumé, company brief) remains data-only.
Detects and labels fake instructions embedded in evidence sources.

Per PROMPT_BOUNDARY_CONTRACT.md §3.2.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from apps_rg.prompt_assembly._pa_boundary import make_pa_boundary_receipt, PABoundaryStatus
from apps_rg.airlocks._otel_spans import airlock_span

_log = logging.getLogger(__name__)


class C0ContentType(str, Enum):
    """Types of C0 evidence content."""

    JD_JSON = "jd_json"
    RESUME_YAML = "resume_yaml"
    RESUME_JSON = "resume_json"
    BRIEF_JSON = "brief_json"
    UNKNOWN = "unknown"


class C0AnomalyClass(str, Enum):
    """Anomaly classes detected in C0 content."""

    FAKE_POLICY_TEXT = "fake_policy_text_in_evidence"
    FAKE_SYSTEM_INSTRUCTIONS = "fake_system_instructions_in_evidence"
    FAKE_TOOL_CALL = "fake_tool_call_in_evidence"
    MODEL_SUBSTITUTION = "model_substitution_attempt"
    OUTPUT_FORMAT_OVERRIDE = "output_format_override_attempt"
    CREDENTIAL_EXFIL = "credential_exfiltration_pattern"
    SUSPICIOUS_MARKDOWN = "suspicious_markdown_in_evidence"


@dataclass(frozen=True)
class C0Provenance:
    """Provenance record for C0 evidence."""

    source_path: str
    content_type: str
    file_hash: str
    byte_size: int
    retrieval_timestamp: str = ""
    retrieval_query: str = ""  # For forward-compat with C0 retrieval


@dataclass(frozen=True)
class C0Anomaly:
    """Detected anomaly in C0 content."""

    anomaly_class: str
    field_path: str  # e.g., "description", "requirements[2]", "brief.notes"
    severity: int  # 1=note, 2=warn, 3=quarantine
    excerpt: str  # truncated excerpt of suspicious content


@dataclass(frozen=True)
class C0AirlockResult:
    """Result of C0 airlock processing."""

    provenance: dict[str, Any]
    content_hash: str
    anomalies: list[dict[str, Any]]
    quarantine_required: bool
    sanitized_content: dict[str, Any] | None
    receipt: dict[str, Any]


class C0Airlock:
    """C0 Evidence Airlock.

    Validates that evidence content is data-only and detects embedded
    instructions or policy overrides. Produces provenance + receipt.
    """

    def __init__(self):
        self._suspicious_patterns = [
            ("ignore previous", C0AnomalyClass.FAKE_SYSTEM_INSTRUCTIONS, 2),
            ("you are now", C0AnomalyClass.FAKE_SYSTEM_INSTRUCTIONS, 2),
            ("system message", C0AnomalyClass.FAKE_SYSTEM_INSTRUCTIONS, 3),
            ("developer message", C0AnomalyClass.FAKE_SYSTEM_INSTRUCTIONS, 3),
            ("call this function", C0AnomalyClass.FAKE_TOOL_CALL, 2),
            ("switch to model", C0AnomalyClass.MODEL_SUBSTITUTION, 2),
            ("change output format", C0AnomalyClass.OUTPUT_FORMAT_OVERRIDE, 2),
            ("<!--", C0AnomalyClass.SUSPICIOUS_MARKDOWN, 1),
            ("-->", C0AnomalyClass.SUSPICIOUS_MARKDOWN, 1),
            ("send to", C0AnomalyClass.CREDENTIAL_EXFIL, 3),
            ("email to", C0AnomalyClass.CREDENTIAL_EXFIL, 3),
        ]

    def process_file(
        self,
        file_path: Path,
        *,
        request_id: str = "",
        run_id: str = "",
        trace_id: str = "",
        route_id: str = "",
    ) -> C0AirlockResult:
        """Process a C0 evidence file through the airlock.

        Args:
            file_path: Path to JD/resume/brief file
            request_id: Request identifier for receipt
            run_id: Run identifier for receipt
            trace_id: Trace identifier for receipt
            route_id: Route identifier for receipt

        Returns:
            C0AirlockResult with provenance, anomalies, and receipt
        """
        content_type = self._detect_content_type(file_path)
        content_bytes = file_path.read_bytes()
        file_hash = hashlib.sha256(content_bytes).hexdigest()[:16]

        try:
            content_text = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content_text = content_bytes.decode("utf-8", errors="replace")

        # Parse to structured form for analysis
        structured = self._parse_content(content_text, content_type)

        # Analyze for anomalies
        anomalies = self._analyze_content(structured, content_type)
        max_severity = max((a.severity for a in anomalies), default=0)
        quarantine = max_severity >= 3

        # Sanitize if quarantine required (remove/flag suspicious fields)
        sanitized = None
        if quarantine:
            sanitized = self._sanitize_content(structured, anomalies)

        provenance = C0Provenance(
            source_path=str(file_path),
            content_type=content_type.value,
            file_hash=file_hash,
            byte_size=len(content_bytes),
            retrieval_timestamp="",  # Pre-loaded files have no retrieval timestamp
            retrieval_query="",  # Forward-compat with C0 retrieval
        )

        # Build receipt
        if quarantine:
            status = PABoundaryStatus.PA_SECURITY_GAP
            reason_codes = ["C0_QUARANTINE", "ANOMALIES_DETECTED"]
        elif anomalies:
            status = PABoundaryStatus.PA_SECURITY_PASS
            reason_codes = ["C0_PASS_WITH_ANOMALIES", "REVIEW_RECOMMENDED"]
        else:
            status = PABoundaryStatus.PA_SECURITY_PASS
            reason_codes = ["C0_CLEAN"]

        receipt = make_pa_boundary_receipt(
            request_id=request_id or "NOT_BOUND",
            run_id=run_id or "NOT_BOUND",
            trace_id=trace_id or "NOT_BOUND",
            route_id=route_id or "NOT_BOUND",
            policy_hash="c0_airlock_v1",
            blueprint_hash=file_hash,
            prompt_hash="NOT_BOUND",  # C0 is not a prompt
            compiled_artifact_hash="NOT_BOUND",
            bom_hash="NOT_BOUND",
            registry_hash="NOT_BOUND",
            template_hash="NOT_BOUND",
            source_refs={
                "content_type": content_type.value,
                "file_path": str(file_path),
                "file_hash": file_hash,
            },
            lineage_refs={
                "airlock": "C0_EVIDENCE",
                "provenance": provenance.source_path,
                "anomaly_count": str(len(anomalies)),
            },
            status=status,
            reason_codes=reason_codes,
            unavailable_fields=["prompt_hash", "compiled_artifact_hash", "bom_hash", "registry_hash", "template_hash"],
        )

        _log.info(
            "[C0] processed: path=%s type=%s anomalies=%d quarantine=%s",
            file_path, content_type.value, len(anomalies), quarantine,
        )

        span_name = "pa.unsafe_payload_rejection" if quarantine else "pa.airlock_security_pass"
        with airlock_span(
            span_name,
            airlock="C0_EVIDENCE",
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            content_type=content_type.value,
            anomaly_count=len(anomalies),
            quarantine=quarantine,
        ):
            pass

        return C0AirlockResult(
            provenance=provenance.__dict__,
            content_hash=file_hash,
            anomalies=[{
                "anomaly_class": a.anomaly_class,
                "field_path": a.field_path,
                "severity": a.severity,
                "excerpt": a.excerpt,
            } for a in anomalies],
            quarantine_required=quarantine,
            sanitized_content=sanitized,
            receipt=receipt.to_dict(),
        )

    def _detect_content_type(self, path: Path) -> C0ContentType:
        """Detect content type from file path and extension."""
        name = path.name.lower()
        suffix = path.suffix.lower()

        if suffix == ".json":
            if "jd" in name or "job" in name:
                return C0ContentType.JD_JSON
            if "brief" in name:
                return C0ContentType.BRIEF_JSON
            if "resume" in name or "cv" in name:
                return C0ContentType.RESUME_JSON
        elif suffix in (".yaml", ".yml"):
            if "resume" in name or "cv" in name or "candidate" in name:
                return C0ContentType.RESUME_YAML

        return C0ContentType.UNKNOWN

    def _parse_content(self, text: str, content_type: C0ContentType) -> dict[str, Any]:
        """Parse content to structured form."""
        if content_type in (C0ContentType.JD_JSON, C0ContentType.BRIEF_JSON, C0ContentType.RESUME_JSON):
            try:
                import json
                return json.loads(text)
            except json.JSONDecodeError:
                return {"_raw": text, "_parse_error": True}
        elif content_type == C0ContentType.RESUME_YAML:
            try:
                import yaml
                return yaml.safe_load(text) or {}
            except Exception:
                return {"_raw": text, "_parse_error": True}
        return {"_raw": text}

    def _analyze_content(
        self,
        structured: dict[str, Any],
        content_type: C0ContentType,
    ) -> list[C0Anomaly]:
        """Analyze content for anomalies."""
        anomalies: list[C0Anomaly] = []

        # Flatten to text fields for scanning
        text_fields = self._extract_text_fields(structured, prefix="")

        for field_path, text in text_fields:
            text_lower = text.lower()
            for pattern, anomaly_class, severity in self._suspicious_patterns:
                if pattern in text_lower:
                    # Find position for excerpt
                    idx = text_lower.find(pattern)
                    excerpt = text[max(0, idx - 30):idx + len(pattern) + 30]
                    anomalies.append(C0Anomaly(
                        anomaly_class=anomaly_class.value,
                        field_path=field_path,
                        severity=severity,
                        excerpt=excerpt,
                    ))

        return anomalies

    def _extract_text_fields(
        self,
        obj: Any,
        prefix: str,
    ) -> list[tuple[str, str]]:
        """Extract all string fields with their paths."""
        results: list[tuple[str, str]] = []

        if isinstance(obj, str):
            results.append((prefix, obj))
        elif isinstance(obj, dict):
            for k, v in obj.items():
                new_prefix = f"{prefix}.{k}" if prefix else k
                results.extend(self._extract_text_fields(v, new_prefix))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                new_prefix = f"{prefix}[{i}]"
                results.extend(self._extract_text_fields(v, new_prefix))

        return results

    def _sanitize_content(
        self,
        structured: dict[str, Any],
        anomalies: list[C0Anomaly],
    ) -> dict[str, Any]:
        """Sanitize content by removing/quarantining suspicious fields."""
        # Deep copy and sanitize
        import copy
        sanitized = copy.deepcopy(structured)

        # Track quarantined paths
        quarantined_paths = [a.field_path for a in anomalies if a.severity >= 2]

        for path in quarantined_paths:
            self._set_field_quarantined(sanitized, path)

        return sanitized

    def _set_field_quarantined(self, obj: Any, path: str) -> None:
        """Mark a field path as quarantined in the sanitized object."""
        parts = path.replace("[", ".").replace("]", "").split(".")

        current = obj
        for part in parts[:-1]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                idx = int(part)
                if idx < len(current):
                    current = current[idx]
            else:
                return  # Path broken

        final = parts[-1]
        if isinstance(current, dict) and final in current:
            original = current[final]
            current[final] = {
                "_C0_QUARANTINED": True,
                "_original_type": type(original).__name__,
                "_original_preview": str(original)[:100],
            }


def process_evidence_file(
    file_path: Path,
    *,
    request_id: str = "",
    run_id: str = "",
    trace_id: str = "",
    route_id: str = "",
) -> C0AirlockResult:
    """Convenience function for C0 airlock processing."""
    airlock = C0Airlock()
    return airlock.process_file(
        file_path,
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        route_id=route_id,
    )


__all__ = [
    "C0Airlock",
    "C0AirlockResult",
    "C0Anomaly",
    "C0AnomalyClass",
    "C0ContentType",
    "C0Provenance",
    "process_evidence_file",
]
