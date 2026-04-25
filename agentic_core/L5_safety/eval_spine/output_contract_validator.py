"""Output-contract validator (ADR-039).

Validates a sealed final artifact against a declared output contract.
Dispatches on ``kind`` to one of the kind-specific validators. Returns a
typed result that populates ``ExitDecision.output_contract``.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

try:
    import jsonschema  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - jsonschema optional
    jsonschema = None  # type: ignore[assignment]


_CONTRACT_ROOT = Path("config/contracts")


class OutputContractError(ValueError):
    """Raised when the contract definition itself is malformed."""


@dataclass(frozen=True)
class ContractResult:
    """Output-contract validation result."""

    required_form_satisfied: bool
    contract_ref: str | None = None
    violations: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "required_form_satisfied": self.required_form_satisfied,
            "contract_ref": self.contract_ref,
            "violations": list(self.violations),
        }


def _load_contract(contract_ref: str, root: Path) -> Mapping[str, Any]:
    path = root / f"{contract_ref}.json"
    if not path.exists():
        # Surface as a contract-resolution violation rather than raising so
        # that the validator always returns a ContractResult.
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, Mapping):
        raise OutputContractError(f"contract root must be an object: {path}")
    return raw


def _validate_none(_artifact: Any, _contract: Mapping[str, Any]) -> list[str]:
    return []


def _validate_json_schema(artifact: Any, contract: Mapping[str, Any]) -> list[str]:
    schema_ref = contract.get("schema_ref")
    if not isinstance(schema_ref, str) or not schema_ref:
        return ["contract.json_schema.missing_schema_ref"]
    schema_path = Path(schema_ref)
    if not schema_path.exists():
        return [f"contract.json_schema.schema_ref_unresolved:{schema_ref}"]
    try:
        with schema_path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"contract.json_schema.schema_read_error:{exc}"]
    if jsonschema is None:
        # Structural fallback: ensure artifact is a dict if schema says object.
        if schema.get("type") == "object" and not isinstance(artifact, Mapping):
            return ["contract.json_schema.artifact_not_object"]
        return []
    try:
        validator = jsonschema.Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(artifact), key=lambda error: error.path)
        return [f"json_schema:{error.message}" for error in errors]
    except jsonschema.SchemaError as exc:  # pragma: no cover - schema author bug
        return [f"contract.json_schema.invalid_schema:{exc.message}"]


def _validate_markdown_sections(artifact: Any, contract: Mapping[str, Any]) -> list[str]:
    if not isinstance(artifact, str):
        return ["contract.markdown_sections.artifact_not_text"]
    required = contract.get("required_sections") or []
    if not isinstance(required, list):
        return ["contract.markdown_sections.required_sections_not_list"]
    violations: list[str] = []
    # Collect existing heading lines in order (ATX only).
    found_headings = [
        line.lstrip("#").strip() for line in artifact.splitlines() if line.lstrip().startswith("#")
    ]
    cursor = 0
    for section in required:
        if not isinstance(section, str):
            violations.append(f"contract.markdown_sections.bad_spec:{section!r}")
            continue
        try:
            idx = next(
                i
                for i, heading in enumerate(found_headings[cursor:], start=cursor)
                if heading.lower() == section.lower()
            )
            cursor = idx + 1
        except StopIteration:
            violations.append(f"contract.markdown_sections.missing_or_out_of_order:{section}")
    return violations


def _validate_tool_result_envelope(artifact: Any, contract: Mapping[str, Any]) -> list[str]:
    if not isinstance(artifact, Mapping):
        return ["contract.tool_result_envelope.artifact_not_object"]
    required_fields = ("success", "payload", "reason", "schema_version")
    missing = [field_ for field_ in required_fields if field_ not in artifact]
    violations: list[str] = [f"contract.tool_result_envelope.missing_field:{field_}" for field_ in missing]
    expected_version = contract.get("envelope_version")
    actual_version = artifact.get("schema_version")
    if isinstance(expected_version, int) and actual_version != expected_version:
        violations.append(
            f"contract.tool_result_envelope.version_mismatch:"
            f"expected={expected_version},actual={actual_version!r}"
        )
    if "success" in artifact and not isinstance(artifact["success"], bool):
        violations.append("contract.tool_result_envelope.success_not_bool")
    return violations


def _validate_text_constraints(artifact: Any, contract: Mapping[str, Any]) -> list[str]:
    if not isinstance(artifact, str):
        return ["contract.text_constraints.artifact_not_text"]
    violations: list[str] = []
    max_chars = contract.get("max_chars")
    min_chars = contract.get("min_chars")
    if isinstance(max_chars, int) and len(artifact) > max_chars:
        violations.append(f"contract.text_constraints.exceeds_max:{len(artifact)}>{max_chars}")
    if isinstance(min_chars, int) and len(artifact) < min_chars:
        violations.append(f"contract.text_constraints.below_min:{len(artifact)}<{min_chars}")
    for pattern in contract.get("regex_denylist") or []:
        if not isinstance(pattern, str):
            continue
        try:
            if re.search(pattern, artifact):
                violations.append(f"contract.text_constraints.matched_denylist:{pattern}")
        except re.error as exc:  # pragma: no cover - author bug
            violations.append(f"contract.text_constraints.bad_regex:{pattern}:{exc}")
    return violations


_VALIDATORS = {
    "none": _validate_none,
    "json_schema": _validate_json_schema,
    "markdown_sections": _validate_markdown_sections,
    "tool_result_envelope": _validate_tool_result_envelope,
    "text_constraints": _validate_text_constraints,
    "proposal_template": _validate_markdown_sections,  # template is sections + text
}


def validate(
    artifact: Any,
    contract_ref: str | None,
    *,
    contract_root: Path | None = None,
) -> ContractResult:
    """Validate ``artifact`` against the contract named by ``contract_ref``.

    A ``contract_ref`` of None or 'none' maps to a trivial pass.
    """
    if contract_ref is None or contract_ref == "none":
        return ContractResult(required_form_satisfied=True, contract_ref=contract_ref)

    root = contract_root or _CONTRACT_ROOT
    try:
        contract = _load_contract(contract_ref, root)
    except FileNotFoundError:
        return ContractResult(
            required_form_satisfied=False,
            contract_ref=contract_ref,
            violations=(f"contract_ref_unresolved:{contract_ref}",),
        )
    kind = contract.get("kind")
    if not isinstance(kind, str):
        return ContractResult(
            required_form_satisfied=False,
            contract_ref=contract_ref,
            violations=("contract.kind_missing",),
        )
    validator = _VALIDATORS.get(kind)
    if validator is None:
        return ContractResult(
            required_form_satisfied=False,
            contract_ref=contract_ref,
            violations=(f"contract.kind_unknown:{kind}",),
        )
    violations = validator(artifact, contract)
    return ContractResult(
        required_form_satisfied=not violations,
        contract_ref=contract_ref,
        violations=tuple(violations),
    )


__all__ = [
    "ContractResult",
    "OutputContractError",
    "validate",
]
