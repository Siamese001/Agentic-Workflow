"""Centralized safety policy stack for v10.8 workflows."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel
from typing_extensions import Literal


class SafetyFinding(BaseModel):
    """Represents a single safety violation emitted by the policy stack."""

    category: Literal["pii", "bias", "injection", "toxicity", "security", "hallucination"]
    message: str
    span: Optional[Tuple[int, int]] = None
    severity: Literal["low", "medium", "high"]


class SafetyReport(BaseModel):
    """Aggregate report combining findings from each detector."""

    findings: List[SafetyFinding]
    is_safe: bool
    blocked_reasons: List[str]
    raw_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "findings": [finding.model_dump() for finding in self.findings],
            "is_safe": self.is_safe,
            "blocked_reasons": list(self.blocked_reasons),
            "raw_text": self.raw_text,
        }


class SafetyPolicyStack:
    """Runs lightweight heuristics over text/node outputs to detect risks."""

    def __init__(self, workflow_context: Any, debug_mode: bool = False) -> None:
        self.workflow_context = workflow_context
        self.debug_mode = debug_mode
        self._pii_patterns = {
            "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            "PHONE": re.compile(r"\b(?:\+?1[ -]?)?(?:\(\d{3}\)|\d{3})[ -]?\d{3}[ -]?\d{4}\b"),
            "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        }
        self._bias_terms = {
            "young",
            "energetic",
            "recent graduate",
            "digital native",
            "male",
            "female",
            "he/she",
            "his/her",
        }
        self._toxicity_terms = {
            "idiot",
            "stupid",
            "hate",
            "worthless",
            "incompetent",
        }
        self._security_terms = {
            "password",
            "secret",
            "api key",
            "apikey",
            "credential",
            "ssh key",
            "token",
        }
        self._injection_terms = {
            "ignore previous instructions",
            "disregard all prior",
            "override the rules",
            "disable safety",
            "exfiltrate",
            "bypass security",
        }
        self._hallucination_markers = {
            "lorem ipsum",
            "to be determined",
            "<placeholder>",
            "???",
            "[unknown]",
        }

    def evaluate_text(self, text: str) -> SafetyReport:
        """Evaluate raw text and return a consolidated report."""

        normalized = text or ""
        detectors = (
            self._detect_pii,
            self._detect_bias,
            self._detect_prompt_injection,
            self._detect_security_risk,
            self._detect_toxicity,
            self._detect_factual_hallucination,
        )
        findings: List[SafetyFinding] = []
        for detector in detectors:
            findings.extend(detector(normalized))
        return self._build_report(findings, normalized)

    def evaluate_node(self, node_output: Dict[str, Any]) -> SafetyReport:
        """Serialize node output and run the standard text evaluation."""

        serialized = self._serialize_node_output(node_output)
        return self.evaluate_text(serialized)

    # ------------------------------------------------------------------
    # Detector implementations
    # ------------------------------------------------------------------

    def _detect_pii(self, text: str) -> List[SafetyFinding]:
        findings: List[SafetyFinding] = []
        for label, pattern in self._pii_patterns.items():
            for match in pattern.finditer(text):
                severity = "high" if label == "SSN" else "medium"
                findings.append(
                    SafetyFinding(
                        category="pii",
                        message=f"Detected {label} pattern",
                        span=(match.start(), match.end()),
                        severity=severity,
                    )
                )
        return findings

    def _detect_bias(self, text: str) -> List[SafetyFinding]:
        findings: List[SafetyFinding] = []
        lowered = text.lower()
        for phrase in self._bias_terms:
            idx = lowered.find(phrase)
            if idx != -1:
                findings.append(
                    SafetyFinding(
                        category="bias",
                        message=f"Potentially biased phrase '{phrase}'",
                        span=(idx, idx + len(phrase)),
                        severity="medium",
                    )
                )
        return findings

    def _detect_prompt_injection(self, text: str) -> List[SafetyFinding]:
        findings: List[SafetyFinding] = []
        lowered = text.lower()
        for phrase in self._injection_terms:
            idx = lowered.find(phrase)
            if idx != -1:
                findings.append(
                    SafetyFinding(
                        category="injection",
                        message=f"Prompt injection attempt via '{phrase}'",
                        span=(idx, idx + len(phrase)),
                        severity="high",
                    )
                )
        return findings

    def _detect_security_risk(self, text: str) -> List[SafetyFinding]:
        findings: List[SafetyFinding] = []
        lowered = text.lower()
        for phrase in self._security_terms:
            idx = lowered.find(phrase)
            if idx != -1:
                findings.append(
                    SafetyFinding(
                        category="security",
                        message=f"Security-sensitive token '{phrase}' present",
                        span=(idx, idx + len(phrase)),
                        severity="high" if phrase in {"password", "ssh key", "secret"} else "medium",
                    )
                )
        return findings

    def _detect_toxicity(self, text: str) -> List[SafetyFinding]:
        findings: List[SafetyFinding] = []
        lowered = text.lower()
        for phrase in self._toxicity_terms:
            idx = lowered.find(phrase)
            if idx != -1:
                findings.append(
                    SafetyFinding(
                        category="toxicity",
                        message=f"Toxic language detected: '{phrase}'",
                        span=(idx, idx + len(phrase)),
                        severity="medium",
                    )
                )
        return findings

    def _detect_factual_hallucination(self, text: str) -> List[SafetyFinding]:
        findings: List[SafetyFinding] = []
        lowered = text.lower()
        for marker in self._hallucination_markers:
            idx = lowered.find(marker)
            if idx != -1:
                findings.append(
                    SafetyFinding(
                        category="hallucination",
                        message=f"Placeholder or unknown marker '{marker}' detected",
                        span=(idx, idx + len(marker)),
                        severity="low",
                    )
                )
        if "i cannot verify" in lowered and "but" in lowered:
            idx = lowered.find("i cannot verify")
            findings.append(
                SafetyFinding(
                    category="hallucination",
                    message="Speculative statement follows an unverifiable claim",
                    span=(idx, idx + len("i cannot verify")),
                    severity="medium",
                )
            )
        return findings

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _serialize_node_output(self, node_output: Any) -> str:
        if node_output is None:
            return ""
        if isinstance(node_output, str):
            return node_output
        if isinstance(node_output, (int, float, bool)):
            return str(node_output)
        try:
            return json.dumps(node_output, ensure_ascii=False, default=str, sort_keys=True)
        except Exception:
            return str(node_output)

    def _build_report(self, findings: List[SafetyFinding], raw_text: str) -> SafetyReport:
        blocked = [f"{finding.category}:{finding.message}" for finding in findings]
        return SafetyReport(
            findings=findings,
            is_safe=len(findings) == 0,
            blocked_reasons=blocked,
            raw_text=raw_text,
        )
