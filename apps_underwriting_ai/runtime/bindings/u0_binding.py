"""U0 ingress validator binding for apps_underwriting_ai.

U0 is the FIRST stage of the
  U0 → L1 → L0 → C0 → PA → L2 → Exit
dispatch chain. Its job:

    1. Load all 17 domain_contract YAML blobs from
       apps_underwriting_ai/config/domain_contract/ once at ingress time.
    2. Package them as a runtime_customization_package dict on the
       ValidatedUnderwritingRequest, making the full domain policy
       available to every downstream layer without re-loading YAML.
    3. Validate required input fields (request_id, applicant_id,
       product_class) — fail-closed on any missing field.
    4. Enforce the input_contract.yaml forbidden_inputs rules
       (protected_attribute_direct_input, non_consented_external_scoring).
    5. Enforce negative_controls.yaml policy violations.
    6. Return a ValidatedUnderwritingRequest — raises on any violation.

Pattern: pure function. No state. No I/O beyond YAML loads from the
canonical config directory. No provider calls. No engine calls.

Plan: apps-underwriting-ai-kill-parallel-pipelines-a3f7e2 W2.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apps_underwriting_ai.runtime.contracts.underwriting_ingress_payload import (
    UnderwritingIngressEnvelope,
    ValidatedUnderwritingRequest,
)

TASK_CLASS: str = "underwriting_decision"
APP_ID: str = "apps_underwriting_ai"
U0_CERT_REF: str = "u0-apps-underwriting-ai-underwriting-decision-a3f7e2"

_CONFIG_DIR = (
    Path(__file__).resolve().parents[2] / "config" / "domain_contract"
)

_DOMAIN_CONTRACT_FILES: tuple[tuple[str, str], ...] = (
    ("app_domain_manifest", "app_domain_manifest.yaml"),
    ("cache_profiles", "cache_profiles.yaml"),
    ("capability_profiles", "capability_profiles.yaml"),
    ("eval_rubrics", "eval_rubrics.yaml"),
    ("fixtures", "fixtures.yaml"),
    ("grader_roster", "grader_roster.yaml"),
    ("input_contract", "input_contract.yaml"),
    ("learning_profiles", "learning_profiles.yaml"),
    ("negative_controls", "negative_controls.yaml"),
    ("orchestration_profiles", "orchestration_profiles.yaml"),
    ("output_schema", "output_schema.yaml"),
    ("prompt_profiles", "prompt_profiles.yaml"),
    ("repair_profiles", "repair_profiles.yaml"),
    ("retrieval_profiles", "retrieval_profiles.yaml"),
    ("route_profiles", "route_profiles.yaml"),
    ("task_classes", "task_classes.yaml"),
    ("threshold_profiles", "threshold_profiles.yaml"),
)


class U0ValidationError(ValueError):
    """Raised when U0 rejects an inbound request. Always fail-closed."""


def _load_domain_contracts(config_dir: Path) -> dict[str, Any]:
    """Load all 17 domain_contract YAMLs into a single dict.

    Raises U0ValidationError if the config directory is missing or any
    required file cannot be parsed. Called once per request.
    """
    if not config_dir.is_dir():
        raise U0ValidationError(
            f"U0: domain_contract config directory not found: {config_dir}. "
            "apps_underwriting_ai/config/domain_contract/ must exist."
        )

    package: dict[str, Any] = {}
    for key, filename in _DOMAIN_CONTRACT_FILES:
        path = config_dir / filename
        if not path.exists():
            raise U0ValidationError(
                f"U0: required domain_contract file missing: {filename} "
                f"(expected at {path})"
            )
        try:
            content = path.read_text(encoding="utf-8")
            package[key] = yaml.safe_load(content)
        except yaml.YAMLError as exc:
            raise U0ValidationError(
                f"U0: failed to parse domain_contract/{filename}: {exc}"
            ) from exc
    return package


def _validate_required_fields(envelope: UnderwritingIngressEnvelope) -> None:
    """Enforce required input fields — fail-closed on any missing field."""
    for field_name in ("request_id", "applicant_id", "product_class"):
        value = getattr(envelope, field_name, None)
        if not value or not str(value).strip():
            raise U0ValidationError(
                f"U0: required field '{field_name}' is missing or empty "
                f"(request_id={envelope.request_id!r}). "
                "apps_underwriting_ai U0 is fail-closed — all required fields must be present."
            )


def _enforce_input_contract(
    envelope: UnderwritingIngressEnvelope,
    input_contract: dict[str, Any],
) -> None:
    """Enforce forbidden_inputs from input_contract.yaml.

    Checks metadata keys against the forbidden_inputs list.
    """
    forbidden = input_contract.get("forbidden_inputs", [])
    metadata = envelope.metadata or {}
    for forbidden_key in forbidden:
        if forbidden_key in metadata:
            raise U0ValidationError(
                f"U0: forbidden input '{forbidden_key}' present in request metadata "
                f"(request_id={envelope.request_id!r}). "
                "apps_underwriting_ai U0 is fail-closed — forbidden inputs must not be submitted."
            )


def _enforce_negative_controls(
    envelope: UnderwritingIngressEnvelope,
    negative_controls: Any,
) -> None:
    """Enforce negative_controls.yaml policy rules.

    negative_controls is a list of control dicts with 'id', 'description',
    and 'blocked_input_keys' fields.
    """
    if not isinstance(negative_controls, list):
        return
    metadata = envelope.metadata or {}
    for control in negative_controls:
        if not isinstance(control, dict):
            continue
        blocked_keys = control.get("blocked_input_keys") or []
        for key in blocked_keys:
            if key in metadata:
                control_id = control.get("id", "unknown")
                raise U0ValidationError(
                    f"U0: negative control '{control_id}' triggered by key '{key}' "
                    f"in request metadata (request_id={envelope.request_id!r}). "
                    "apps_underwriting_ai U0 is fail-closed — policy violations block execution."
                )


def u0_validate_underwriting(
    envelope: UnderwritingIngressEnvelope,
    *,
    config_dir: Path | None = None,
) -> ValidatedUnderwritingRequest:
    """Validate an UnderwritingIngressEnvelope and produce a ValidatedUnderwritingRequest.

    Pipeline:
        1. Load all 17 domain_contract YAMLs → runtime_customization_package.
        2. Validate required fields (request_id, applicant_id, product_class).
        3. Enforce input_contract.yaml forbidden_inputs.
        4. Enforce negative_controls.yaml policy rules.
        5. Return ValidatedUnderwritingRequest carrying full package + top-level
           convenience fields (app_domain_manifest, input_contract,
           route_profiles, threshold_profiles, policy_hash, blueprint_hash).

    Args:
        envelope: The UnderwritingIngressEnvelope built by __main__.py or
            the API ingress layer.
        config_dir: Override for the domain_contract directory (for tests).
            Defaults to apps_underwriting_ai/config/domain_contract/.

    Returns:
        ValidatedUnderwritingRequest ready for L1+.

    Raises:
        U0ValidationError: on any validation failure. Always fail-closed.
        TypeError: if envelope is not an UnderwritingIngressEnvelope.
    """
    if not isinstance(envelope, UnderwritingIngressEnvelope):
        raise TypeError(
            f"u0_validate_underwriting expected UnderwritingIngressEnvelope, "
            f"got {type(envelope).__name__}"
        )

    effective_config_dir = config_dir if config_dir is not None else _CONFIG_DIR

    package = _load_domain_contracts(effective_config_dir)

    _validate_required_fields(envelope)
    _enforce_input_contract(envelope, package.get("input_contract") or {})
    _enforce_negative_controls(envelope, package.get("negative_controls"))

    manifest = package.get("app_domain_manifest") or {}
    route_profiles = package.get("route_profiles") or []
    if not isinstance(route_profiles, list):
        route_profiles = [route_profiles]
    threshold_profiles = package.get("threshold_profiles") or []
    if not isinstance(threshold_profiles, list):
        threshold_profiles = [threshold_profiles]

    return ValidatedUnderwritingRequest(
        request_id=envelope.request_id,
        applicant_id=envelope.applicant_id,
        product_class=envelope.product_class,
        documents=tuple(envelope.documents),
        metadata=dict(envelope.metadata),
        trace_id=envelope.trace_id,
        submitted_at=envelope.submitted_at,
        runtime_customization_package=package,
        app_domain_manifest=manifest,
        input_contract=package.get("input_contract") or {},
        route_profiles=route_profiles,
        threshold_profiles=threshold_profiles,
        policy_hash=str(manifest.get("policy_hash", "")),
        blueprint_hash=str(manifest.get("blueprint_hash", "")),
        task_class=TASK_CLASS,
        app_id=APP_ID,
        u0_cert_ref=U0_CERT_REF,
    )


__all__ = [
    "TASK_CLASS",
    "APP_ID",
    "U0_CERT_REF",
    "U0ValidationError",
    "u0_validate_underwriting",
]
