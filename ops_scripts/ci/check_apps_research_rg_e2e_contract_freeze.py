#!/usr/bin/env python3
"""Fail-closed validation for the issue #550 Wave 0 authority-contract freeze."""

from __future__ import annotations

import ast
import copy
import json
import re
import sys
from collections import deque
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = Path(
    "config/certification/apps_research_rg_e2e_authority_contract.v1.json"
)
EXPECTED_CONTRACT_ID = "apps_research_rg_e2e_authority"
EXPECTED_SCHEMA_VERSION = "apps_research_rg_e2e_authority_contract.v1"
EXPECTED_IDENTITY_PROFILE = "apps_research_rg_run_identity.v1"
EXPECTED_IDENTITY_FIELDS = (
    "producer_app_id",
    "consumer_app_id",
    "parent_run_id",
    "child_run_id",
    "request_id",
    "trace_root",
    "tenant_id",
    "target_company",
    "target_role",
    "jd_sha256",
    "brief_sha256",
    "policy_hash",
    "blueprint_hash",
    "schema_version",
)
EXPECTED_X3_CODES = (
    "X3A_DENY_REROUTE",
    "X3B_ESCALATE_HITL",
    "X3C_COMMIT_REQUEST_TO_UWG",
    "X3D_ALLOW_FINISH",
    "X3E_SAFE_ABSTAIN",
)
EXPECTED_CURRENT_RUN_AUTHORITIES = (
    "FRESH_PREFLIGHT",
    "APPS_RESEARCH_EXIT",
    "APPS_RG_U0",
    "APPS_RG_EXIT",
    "PRODUCT_ELIGIBILITY",
    "UWG",
)
EXPECTED_POST_BOUNDARY_OBSERVERS = (
    "APPS_EVAL",
    "L6_SHADOW",
    "FUTURE_RUN_PROMOTION",
)
EXPECTED_STAGE_IDS = (
    "FRESH_PREFLIGHT",
    "APPS_RESEARCH_U0",
    "APPS_RESEARCH_RUNTIME",
    "APPS_RESEARCH_EXIT",
    "HANDOFF_BUNDLE_COMMIT",
    "APPS_RG_U0",
    "APPS_RG_L1",
    "APPS_RG_L0",
    "APPS_RG_C0",
    "APPS_RG_PA",
    "APPS_RG_L2",
    "X1_REVIEW",
    "X2_AGGREGATION",
    "X3_DISPOSITION",
    "PRODUCT_ELIGIBILITY",
    "UWG_COMMIT",
    "PRODUCT_AUTHORIZATION_CLOSE",
    "APPS_EVAL",
    "L6_SHADOW",
    "INDEPENDENT_PARITY",
    "PROMOTION_TERMINAL",
    "MANDATORY_OUTPUTS",
    "STAGE_LEDGER_SEAL",
    "TERMINAL_MANIFEST_SEAL",
    "PIPELINE_COMPLETION_CLOSE",
    "TERMINAL_NON_PRODUCT",
)
EXPECTED_ENTRYPOINT_IDS = (
    "apps_research_product_cli",
    "apps_research_e2e_live_certification",
    "apps_research_dry_run",
    "apps_rg_fresh_e2e_product_cli",
    "apps_rg_default_whole_run_cli",
    "apps_rg_section_cli",
    "apps_rg_patch_run",
    "apps_rg_assemble_from_pinned",
    "apps_rg_whole_run_orchestrator",
    "agentic_core_single_action_spine",
    "apps_rg_post_x3_finalize",
    "apps_eval_live_adapter",
    "apps_eval_snapshot",
    "apps_eval_matrix",
    "apps_eval_baseline_promotion",
    "apps_rg_l6_shadow_runner",
)
EXPECTED_PRODUCT_REQUIREMENTS = (
    "fresh_preflight_continuation_valid",
    "producer_chain_valid_when_delegated",
    "apps_rg_u0_through_l2_complete",
    "x1_x2_authoritative_receipts_pass",
    "x3_code_exactly_X3D_ALLOW_FINISH",
    "product_eligibility_pass",
    "uwg_commit_receipt_bound_to_output_bytes",
)
EXPECTED_PIPELINE_REQUIREMENTS = (
    "product_authorized_true",
    "apps_eval_sealed_read_only_snapshot_complete",
    "l6_closure_complete",
    "apps_eval_l6_identity_and_byte_parity_pass",
    "promotion_terminal_status_present",
    "mandatory_outputs_digest_bound",
    "stage_ledger_v2_complete_and_sealed",
    "terminal_manifest_v1_sealed_last",
)
POST_BOUNDARY_STAGE_IDS = frozenset(
    {
        "APPS_EVAL",
        "L6_SHADOW",
        "INDEPENDENT_PARITY",
        "PROMOTION_TERMINAL",
        "MANDATORY_OUTPUTS",
        "STAGE_LEDGER_SEAL",
        "TERMINAL_MANIFEST_SEAL",
        "PIPELINE_COMPLETION_CLOSE",
    }
)
EXPECTED_SCHEMA_REGISTRY = {
    "apps_research.apps_rg_handoff.v2": (
        "config/certification/schemas/"
        "apps_research_apps_rg_handoff.v2.schema.json"
    ),
    "apps_rg.e2e_stage_ledger.v2": (
        "config/certification/schemas/apps_rg_e2e_stage_ledger.v2.schema.json"
    ),
    "apps_rg.e2e_terminal_manifest.v1": (
        "config/certification/schemas/apps_rg_e2e_terminal_manifest.v1.schema.json"
    ),
}
REQUIRED_WORKFLOW_PATHS = (
    "docs/architecture/adr/ADR-106-apps-research-rg-e2e-authority-contract.md",
    str(CONTRACT_PATH),
    *EXPECTED_SCHEMA_REGISTRY.values(),
    "ops_scripts/ci/check_apps_research_rg_e2e_contract_freeze.py",
    "tests/unit/ops_scripts/ci/test_apps_research_rg_e2e_contract_freeze.py",
)
REFERENCE_FIELDS = ("producer", "consumer", "schema_ref")
STAGE_REQUIRED_FIELDS = {
    "stage_id",
    "authority_plane",
    "producer",
    "consumer",
    "authoritative_receipt",
    "schema_ref",
    "identity_profile",
    "allowed_next",
    "pass_derivation",
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return payload


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def _canonical_x3_codes(repo_root: Path) -> tuple[str, ...]:
    source_path = repo_root / "agentic_core/runtime/exit/exit_disposition.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    values: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if (
            isinstance(target, ast.Name)
            and re.fullmatch(r"X3[A-E]_[A-Z0-9_]+", target.id)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            values[target.id] = node.value.value
    return tuple(values[name] for name in sorted(values))


def _reference_path(reference: str, registry: dict[str, str]) -> str | None:
    if reference == "CALLER":
        return None
    base_reference = reference.split("#", 1)[0]
    resolved = registry.get(base_reference, registry.get(reference, base_reference))
    return resolved.split("#", 1)[0].split(":", 1)[0]


def _reference_symbol(reference: str, registry: dict[str, str]) -> str | None:
    if reference in registry or "#" in reference or ":" not in reference:
        return None
    path, symbol = reference.split(":", 1)
    return symbol if path.endswith(".py") and symbol else None


def _top_level_symbols(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def _local_json_pointer_exists(document: dict[str, Any], reference: str) -> bool:
    if reference == "#":
        return True
    if not reference.startswith("#/"):
        return False
    current: Any = document
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def _schema_structure_errors(schema: dict[str, Any], relative_path: str) -> list[str]:
    """Check local references and critical keyword shapes without a runtime dependency."""

    errors: list[str] = []
    valid_types = {"array", "boolean", "integer", "null", "number", "object", "string"}

    def visit(value: Any, location: str, *, schema_map: bool = False) -> None:
        if isinstance(value, list):
            for index, item in enumerate(value):
                visit(item, f"{location}/{index}")
            return
        if not isinstance(value, dict):
            return
        if schema_map:
            for name, item in value.items():
                visit(item, f"{location}/{name}")
            return
        reference = value.get("$ref")
        if isinstance(reference, str) and not _local_json_pointer_exists(schema, reference):
            errors.append(f"{relative_path}{location}: unresolved or external $ref {reference}")
        declared_type = value.get("type")
        if isinstance(declared_type, str) and declared_type not in valid_types:
            errors.append(f"{relative_path}{location}: invalid type {declared_type}")
        if isinstance(declared_type, list) and (
            not declared_type or any(item not in valid_types for item in declared_type)
        ):
            errors.append(f"{relative_path}{location}: invalid type union")
        required = value.get("required")
        if required is not None and (
            not isinstance(required, list)
            or any(not isinstance(item, str) for item in required)
        ):
            errors.append(f"{relative_path}{location}: required must be a string list")
        properties = value.get("properties")
        if properties is not None and not isinstance(properties, dict):
            errors.append(f"{relative_path}{location}: properties must be an object")
        for keyword in ("allOf", "anyOf", "oneOf"):
            variants = value.get(keyword)
            if variants is not None and (
                not isinstance(variants, list) or not variants
            ):
                errors.append(f"{relative_path}{location}: {keyword} must be a non-empty list")
        for key, item in value.items():
            visit(
                item,
                f"{location}/{key}",
                schema_map=key
                in {"$defs", "dependentSchemas", "patternProperties", "properties"},
            )

    visit(schema, "")
    return errors


def _reachable_stage_ids(stages: dict[str, dict[str, Any]]) -> set[str]:
    if "FRESH_PREFLIGHT" not in stages:
        return set()
    seen: set[str] = set()
    queue: deque[str] = deque(["FRESH_PREFLIGHT"])
    while queue:
        stage_id = queue.popleft()
        if stage_id in seen or stage_id not in stages:
            continue
        seen.add(stage_id)
        for next_stage in stages[stage_id].get("allowed_next", []):
            if isinstance(next_stage, str) and next_stage not in seen:
                queue.append(next_stage)
    return seen


def _validate_schema_registry(
    document: dict[str, Any], repo_root: Path, errors: list[str]
) -> None:
    registry = document.get("schema_registry")
    if registry != EXPECTED_SCHEMA_REGISTRY:
        errors.append("schema_registry must exactly match the three frozen schema paths")
        return

    for schema_id, relative_path in EXPECTED_SCHEMA_REGISTRY.items():
        path = repo_root / relative_path
        if not path.is_file():
            errors.append(f"schema missing: {relative_path}")
            continue
        try:
            schema = _load_json(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"schema invalid: {relative_path}: {exc}")
            continue
        errors.extend(_schema_structure_errors(schema, relative_path))
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{relative_path}: must use JSON Schema draft 2020-12")
        if schema.get("$id") != schema_id:
            errors.append(f"{relative_path}: $id must be {schema_id}")
        version_const = (
            schema.get("properties", {}).get("schema_version", {}).get("const")
        )
        if version_const != schema_id:
            errors.append(f"{relative_path}: schema_version const must be {schema_id}")
        identity = schema.get("$defs", {}).get("RunIdentity", {})
        if tuple(identity.get("required", ())) != EXPECTED_IDENTITY_FIELDS:
            errors.append(f"{relative_path}: RunIdentity.required drifted")
        identity_const = (
            identity.get("properties", {}).get("schema_version", {}).get("const")
        )
        if identity_const != EXPECTED_IDENTITY_PROFILE:
            errors.append(f"{relative_path}: identity schema_version drifted")

    handoff_path = repo_root / EXPECTED_SCHEMA_REGISTRY[
        "apps_research.apps_rg_handoff.v2"
    ]
    if handoff_path.is_file():
        handoff = _load_json(handoff_path)
        required_fields = set(handoff.get("required", ()))
        required_handoff_fields = {
            "identity",
            "raw_input",
            "normalized_input",
            "mandatory_gate_receipts",
            "exit_authorization",
            "artifact_manifest",
            "commit_protocol",
        }
        if not required_handoff_fields <= required_fields:
            errors.append("handoff v2 dropped a frozen identity, evidence, or commit field")
        gate_keys = tuple(
            handoff.get("$defs", {})
            .get("MandatoryGateReceipts", {})
            .get("required", ())
        )
        if gate_keys != ("G5", "G6", "G7", "G21", "G24", "G26"):
            errors.append("handoff v2 mandatory gate set must be exactly G5/G6/G7/G21/G24/G26")
        exit_code = (
            handoff.get("$defs", {})
            .get("ExitAuthorization", {})
            .get("properties", {})
            .get("x3_code", {})
            .get("const")
        )
        if exit_code != "X3D_ALLOW_FINISH":
            errors.append("handoff v2 must require exact X3D_ALLOW_FINISH authorization")
        consumer_required = set(
            handoff.get("$defs", {}).get("ConsumerValidationReceipt", {}).get("required", ())
        )
        if not {
            "identity",
            "raw_input_sha256",
            "normalized_input_sha256",
            "bundle_manifest_sha256",
            "commit_marker_sha256",
            "artifact_validations",
            "status",
        } <= consumer_required:
            errors.append("handoff v2 consumer validation receipt dropped byte bindings")

    ledger_path = repo_root / EXPECTED_SCHEMA_REGISTRY["apps_rg.e2e_stage_ledger.v2"]
    if ledger_path.is_file():
        ledger = _load_json(ledger_path)
        schema_stages = tuple(
            ledger.get("$defs", {}).get("StageId", {}).get("enum", ())
        )
        if schema_stages != EXPECTED_STAGE_IDS:
            errors.append("stage-ledger v2 StageId enum drifted from the frozen matrix")
        derivation = (
            ledger.get("$defs", {})
            .get("StageEntry", {})
            .get("properties", {})
            .get("status_derivation", {})
            .get("const")
        )
        if derivation != "AUTHORITATIVE_RECEIPT_BYTES":
            errors.append("stage-ledger v2 status must derive from authoritative receipt bytes")
        entry_required = set(
            ledger.get("$defs", {}).get("StageEntry", {}).get("required", ())
        )
        if not {
            "authoritative_receipt_ref",
            "authoritative_receipt_sha256",
            "identity_sha256",
            "artifact_bindings",
        } <= entry_required:
            errors.append("stage-ledger v2 entries must bind receipt, identity, and artifact bytes")

    manifest_path = repo_root / EXPECTED_SCHEMA_REGISTRY[
        "apps_rg.e2e_terminal_manifest.v1"
    ]
    if manifest_path.is_file():
        manifest = _load_json(manifest_path)
        immutable = (
            manifest.get("$defs", {})
            .get("ProductAuthorization", {})
            .get("properties", {})
            .get("immutable", {})
            .get("const")
        )
        if immutable is not True:
            errors.append("terminal manifest must mark product authorization immutable")
        sealed_last = (
            manifest.get("$defs", {})
            .get("ManifestSeal", {})
            .get("properties", {})
            .get("sealed_after_stage_ledger", {})
            .get("const")
        )
        if sealed_last is not True:
            errors.append("terminal manifest must seal after the stage ledger")


def validate_contract_document(
    document: dict[str, Any], repo_root: Path = REPO_ROOT
) -> list[str]:
    """Return all contract-freeze violations without importing runtime modules."""

    errors: list[str] = []
    if document.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        errors.append(f"schema_version must be {EXPECTED_SCHEMA_VERSION}")
    if document.get("contract_id") != EXPECTED_CONTRACT_ID:
        errors.append(f"contract_id must be {EXPECTED_CONTRACT_ID}")
    baseline = document.get("baseline_commit")
    if not isinstance(baseline, str) or re.fullmatch(r"[0-9a-f]{40}", baseline) is None:
        errors.append("baseline_commit must be a full lowercase git SHA")

    authority = document.get("authority_model", {})
    if authority.get("current_run_boundary") != "UWG_COMMIT_CLOSED":
        errors.append("current-run authority boundary must be UWG_COMMIT_CLOSED")
    if authority.get("post_boundary_starts_at") != "APPS_EVAL":
        errors.append("post-boundary observer chain must start at APPS_EVAL")
    if tuple(authority.get("current_run_authorities", ())) != EXPECTED_CURRENT_RUN_AUTHORITIES:
        errors.append("current-run authority owners drifted")
    if tuple(authority.get("post_boundary_observers", ())) != EXPECTED_POST_BOUNDARY_OBSERVERS:
        errors.append("post-boundary observer owners drifted")
    if authority.get("post_boundary_may_change_product_authorization") is not False:
        errors.append("post-boundary observers may not change product authorization")
    if authority.get("unknown_is_pass") is not False:
        errors.append("UNKNOWN may not be interpreted as PASS")
    if authority.get("missing_identity_may_be_synthesized") is not False:
        errors.append("missing product identity may not be synthesized")

    identity = document.get("canonical_identity_profile", {})
    if identity.get("profile_id") != EXPECTED_IDENTITY_PROFILE:
        errors.append("canonical identity profile ID drifted")
    if tuple(identity.get("required_fields", ())) != EXPECTED_IDENTITY_FIELDS:
        errors.append("canonical identity required fields drifted")
    if identity.get("missing_field_disposition") != "BLOCKED":
        errors.append("missing canonical identity must be BLOCKED")

    taxonomy = document.get("x3_taxonomy", {})
    rows = taxonomy.get("codes", [])
    row_codes = tuple(row.get("code") for row in rows if isinstance(row, dict))
    if row_codes != EXPECTED_X3_CODES:
        errors.append("X3 taxonomy must contain the five canonical codes in order")
    try:
        source_codes = _canonical_x3_codes(repo_root)
    except (OSError, SyntaxError) as exc:
        errors.append(f"cannot read canonical X3 source: {exc}")
    else:
        if source_codes != EXPECTED_X3_CODES:
            errors.append("canonical X3 constants in exit_disposition.py drifted")
    if taxonomy.get("product_success_codes") != ["X3D_ALLOW_FINISH"]:
        errors.append("product success must be exactly X3D_ALLOW_FINISH; aliases are forbidden")
    if taxonomy.get("legacy_aliases_allowed_on_product_v2") is not False:
        errors.append("legacy X3 aliases must remain forbidden on product v2")
    aliases = taxonomy.get("legacy_aliases", [])
    if set(aliases) & set(taxonomy.get("product_success_codes", [])):
        errors.append("legacy X3 alias leaked into product_success_codes")

    terminal = document.get("terminal_semantics", {})
    product = terminal.get("product_authorized", {})
    pipeline = terminal.get("pipeline_complete", {})
    repair = terminal.get("observability_repair_required", {})
    if product.get("immutable_after") != "UWG_COMMIT_CLOSED":
        errors.append("product authorization must become immutable at UWG_COMMIT_CLOSED")
    if tuple(product.get("true_requires", ())) != EXPECTED_PRODUCT_REQUIREMENTS:
        errors.append("product_authorized requirements drifted")
    if product.get("post_boundary_can_rescue") is not False:
        errors.append("post-boundary observers may not rescue product authorization")
    if product.get("post_boundary_can_veto") is not False:
        errors.append("post-boundary observers may not veto product authorization")
    if tuple(pipeline.get("true_requires", ())) != EXPECTED_PIPELINE_REQUIREMENTS:
        errors.append("pipeline_complete requirements drifted")
    if repair.get("may_change_product_authorized") is not False:
        errors.append("observability repair may not change product authorization")

    registry = document.get("schema_registry", {})
    if not isinstance(registry, dict):
        errors.append("schema_registry must be an object")
        registry = {}

    stage_rows = document.get("stages", [])
    if not isinstance(stage_rows, list):
        errors.append("stages must be a list")
        stage_rows = []
    stage_ids = [
        row.get("stage_id", "") for row in stage_rows if isinstance(row, dict)
    ]
    if _duplicates(stage_ids):
        errors.append(f"duplicate stage IDs: {_duplicates(stage_ids)}")
    if tuple(stage_ids) != EXPECTED_STAGE_IDS:
        errors.append("stage matrix must contain every frozen stage exactly once and in order")
    stages = {
        row["stage_id"]: row
        for row in stage_rows
        if isinstance(row, dict) and isinstance(row.get("stage_id"), str)
    }
    for index, row in enumerate(stage_rows):
        if not isinstance(row, dict):
            errors.append(f"stage row {index} must be an object")
            continue
        stage_id = row.get("stage_id", f"row-{index}")
        missing = sorted(STAGE_REQUIRED_FIELDS - row.keys())
        if missing:
            errors.append(f"{stage_id}: missing fields {missing}")
        if row.get("authority_plane") not in {"current_run", "post_boundary"}:
            errors.append(f"{stage_id}: invalid authority_plane")
        expected_plane = (
            "post_boundary" if stage_id in POST_BOUNDARY_STAGE_IDS else "current_run"
        )
        if row.get("authority_plane") != expected_plane:
            errors.append(f"{stage_id}: authority_plane must be {expected_plane}")
        if row.get("identity_profile") != EXPECTED_IDENTITY_PROFILE:
            errors.append(f"{stage_id}: identity profile drifted")
        allowed_next = row.get("allowed_next")
        if not isinstance(allowed_next, list):
            errors.append(f"{stage_id}: allowed_next must be a list")
        else:
            unknown = sorted(set(allowed_next) - set(EXPECTED_STAGE_IDS))
            if unknown:
                errors.append(f"{stage_id}: unknown allowed_next stages {unknown}")
        planned = str(row.get("implementation_status", "")).startswith("planned_wave_")
        for field in REFERENCE_FIELDS:
            reference = row.get(field)
            if not isinstance(reference, str) or not reference:
                continue
            relative_path = _reference_path(reference, registry)
            if relative_path is None:
                continue
            path = repo_root / relative_path
            if not path.is_file():
                if not planned:
                    errors.append(f"{stage_id}: {field} path missing: {relative_path}")
                continue
            symbol = _reference_symbol(reference, registry)
            if symbol is not None:
                try:
                    symbols = _top_level_symbols(path)
                except (OSError, SyntaxError) as exc:
                    errors.append(f"{stage_id}: cannot inspect {relative_path}: {exc}")
                else:
                    if symbol not in symbols:
                        errors.append(
                            f"{stage_id}: {field} symbol missing: {relative_path}:{symbol}"
                        )
    unreachable = sorted(set(EXPECTED_STAGE_IDS) - _reachable_stage_ids(stages))
    if unreachable:
        errors.append(f"stages unreachable from FRESH_PREFLIGHT: {unreachable}")

    entrypoint_rows = document.get("entrypoints", [])
    if not isinstance(entrypoint_rows, list):
        errors.append("entrypoints must be a list")
        entrypoint_rows = []
    entrypoint_ids = [
        row.get("entrypoint_id", "")
        for row in entrypoint_rows
        if isinstance(row, dict)
    ]
    if _duplicates(entrypoint_ids):
        errors.append(f"duplicate entrypoint IDs: {_duplicates(entrypoint_ids)}")
    if tuple(entrypoint_ids) != EXPECTED_ENTRYPOINT_IDS:
        errors.append("entrypoint matrix must contain every frozen entrypoint exactly once")
    for index, row in enumerate(entrypoint_rows):
        if not isinstance(row, dict):
            errors.append(f"entrypoint row {index} must be an object")
            continue
        entrypoint_id = row.get("entrypoint_id", f"row-{index}")
        classification = row.get("classification")
        plane = row.get("authority_plane")
        if classification not in {"product", "test", "replay", "migration"}:
            errors.append(f"{entrypoint_id}: invalid classification")
        if plane not in {"current_run", "post_boundary", "none"}:
            errors.append(f"{entrypoint_id}: invalid authority_plane")
        if row.get("authority_contract_id") != EXPECTED_CONTRACT_ID:
            errors.append(f"{entrypoint_id}: must bind the canonical authority contract")
        if row.get("required_start_stage") not in EXPECTED_STAGE_IDS:
            errors.append(f"{entrypoint_id}: unknown required_start_stage")
        success_codes = row.get("required_x3_success_codes")
        product_authority = row.get("product_authority")
        if classification == "product" and plane == "current_run":
            if product_authority is not True:
                errors.append(f"{entrypoint_id}: current-run product path needs product authority")
            if success_codes != ["X3D_ALLOW_FINISH"]:
                errors.append(f"{entrypoint_id}: product success must be exact X3D_ALLOW_FINISH")
        else:
            if product_authority is not False:
                errors.append(f"{entrypoint_id}: non-authority path cannot claim product authority")
            if success_codes != []:
                errors.append(f"{entrypoint_id}: non-authority path cannot define product success")
        implementation = row.get("implementation")
        if isinstance(implementation, str) and implementation:
            relative_path = _reference_path(implementation, registry)
            if relative_path is not None:
                path = repo_root / relative_path
                if not path.is_file():
                    errors.append(f"{entrypoint_id}: implementation path missing: {relative_path}")
                else:
                    symbol = _reference_symbol(implementation, registry)
                    if symbol and symbol not in _top_level_symbols(path):
                        errors.append(f"{entrypoint_id}: implementation symbol missing: {symbol}")

    _validate_schema_registry(document, repo_root, errors)

    migration = document.get("migration_policy", {})
    if migration.get("legacy_x3_aliases_product_path_allowed") is not False:
        errors.append("migration may not enable legacy X3 aliases on product paths")
    if migration.get("non_product_bypass_must_be_explicitly_classified") is not True:
        errors.append("non-product bypasses must remain explicitly classified")

    adr_ref = document.get("adr_ref")
    if not isinstance(adr_ref, str) or not (repo_root / adr_ref).is_file():
        errors.append("adr_ref must resolve to the accepted authority ADR")
    workflow_path = repo_root / ".github/workflows/apps-research-rg-handoff-e2e.yml"
    if not workflow_path.is_file():
        errors.append("canonical handoff workflow is missing")
    else:
        workflow_text = workflow_path.read_text(encoding="utf-8")
        for required_path in REQUIRED_WORKFLOW_PATHS:
            if required_path not in workflow_text:
                errors.append(f"workflow coverage missing: {required_path}")
        command = "python ops_scripts/ci/check_apps_research_rg_e2e_contract_freeze.py"
        if command not in workflow_text:
            errors.append("workflow does not execute the contract-freeze checker")
        negative_controls = (
            "python -m unittest "
            "tests.unit.ops_scripts.ci.test_apps_research_rg_e2e_contract_freeze -v"
        )
        if negative_controls not in workflow_text:
            errors.append("workflow does not execute the contract-freeze negative controls")

    return errors


def validate_contract(
    contract_path: Path = CONTRACT_PATH, repo_root: Path = REPO_ROOT
) -> list[str]:
    try:
        document = _load_json(repo_root / contract_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"cannot load authority contract: {exc}"]
    return validate_contract_document(copy.deepcopy(document), repo_root)


def main() -> int:
    errors = validate_contract()
    result = {
        "contract": str(CONTRACT_PATH),
        "status": "PASS" if not errors else "FAIL",
        "error_count": len(errors),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
