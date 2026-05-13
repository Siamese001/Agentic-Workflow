"""Ingress payload contracts for apps_underwriting_ai U0 binding.

Defines the inbound envelope (CLI/API → U0) and the validated request
(U0 → L1+) shapes for the underwriting decisioning task class.

These contracts replace the deleted ExecutionRequest / ExecutionAdapter /
UnderwritingIngressRunner parallel path.
Plan: apps-underwriting-ai-kill-parallel-pipelines-a3f7e2 W2.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UnderwritingIngressEnvelope:
    """Raw inbound envelope from CLI or API before U0 validation.

    Built by __main__.py or the API ingress layer. Not yet validated.
    All fields are exactly what the caller submitted.
    """

    request_id: str
    applicant_id: str
    product_class: str
    documents: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""
    submitted_at: str = ""


@dataclass
class ValidatedUnderwritingRequest:
    """Validated request produced by U0 — safe to forward to L1+.

    Carries the full runtime_customization_package (all 17 domain_contract
    YAML blobs loaded and validated at U0 time) so every downstream layer
    reads policy from the package rather than re-loading YAML from disk.

    Fail-closed: U0 raises on any validation failure; this dataclass is
    only constructed when all checks pass.
    """

    request_id: str
    applicant_id: str
    product_class: str
    documents: tuple[dict[str, Any], ...]
    metadata: dict[str, Any]
    trace_id: str
    submitted_at: str

    runtime_customization_package: dict[str, Any] = field(default_factory=dict)

    app_domain_manifest: dict[str, Any] = field(default_factory=dict)
    input_contract: dict[str, Any] = field(default_factory=dict)
    route_profiles: list[dict[str, Any]] = field(default_factory=list)
    threshold_profiles: list[dict[str, Any]] = field(default_factory=list)
    policy_hash: str = ""
    blueprint_hash: str = ""

    task_class: str = "underwriting_decision"
    app_id: str = "apps_underwriting_ai"
    u0_cert_ref: str = ""
