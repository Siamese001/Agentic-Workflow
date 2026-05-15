"""apps_rg V1 ingress contract — AppsRgIngressContractV1 + RuntimeCustomizationPackage.

RuntimeCustomizationPackage carries all refs for the U0 layer (24 fields).
It is Pydantic v2 frozen + extra=forbid so stale field names are caught
at construction time.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

try:
    from pydantic import BaseModel, ConfigDict, Field
    _PYDANTIC_AVAILABLE = True
except ImportError:
    _PYDANTIC_AVAILABLE = False

__all__ = [
    "AppsRgIngressContractV1",
    "RuntimeCustomizationPackage",
    "APPS_RG_INGRESS_CONTRACT_VERSION",
    "APPS_RG_FIELD_MAP_SCHEMA_PATH",
    "APPS_RG_INGRESS_SCHEMA_PATH",
]

APPS_RG_INGRESS_CONTRACT_VERSION: str = "v1"

_CONTRACTS_DIR = Path(__file__).resolve().parent
APPS_RG_FIELD_MAP_SCHEMA_PATH = _CONTRACTS_DIR / "apps_rg_ingress_field_map.v1.yaml"
APPS_RG_INGRESS_SCHEMA_PATH = _CONTRACTS_DIR / "apps_rg_ingress_contract.v1.schema.json"


if _PYDANTIC_AVAILABLE:
    class RuntimeCustomizationPackage(BaseModel):
        """U0 runtime customization package — 24 required ref fields."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        workflow_manifest_ref: str = ""
        runtime_gate_profile_ref: str = ""
        exit_profile_ref: str = ""
        judge_profile_ref: str = ""
        eval_rubric_ref: str = ""
        threshold_profile_ref: str = ""
        grader_roster_ref: str = ""
        rubric_output_map_ref: str = ""
        negative_controls_ref: str = ""
        learning_profile_ref: str = ""
        meta_feedback_profile_ref: str = ""
        prompt_profile_ref: str = ""
        route_profile_ref: str = ""
        retrieval_profile_ref: str = ""
        repair_profile_ref: str = ""
        cache_profile_ref: str = ""
        capability_profile_ref: str = ""
        orchestration_profile_ref: str = ""
        provider_profile_ref: str = ""
        write_policy: str = "read_only"
        required_runtime_gates: tuple[str, ...] = ()
        required_exit_gates: tuple[str, ...] = ()
        conditional_exit_gates: tuple[str, ...] = ()
        package_digest: str = ""

    class AppsRgIngressContractV1(BaseModel):
        """Top-level V1 ingress payload for the apps_rg pipeline."""

        model_config = ConfigDict(extra="ignore")

        apps_rg_contract_version: str = APPS_RG_INGRESS_CONTRACT_VERSION
        transport: dict[str, Any] = Field(default_factory=dict)
        identity: dict[str, Any] = Field(default_factory=dict)
        replay: dict[str, Any] = Field(default_factory=dict)
        jd_payload: dict[str, Any] = Field(default_factory=dict)
        resume_payload: dict[str, Any] = Field(default_factory=dict)
        target: dict[str, Any] = Field(default_factory=dict)
        generation_mode: str = "strategic_tailor"
        profile_manifest: dict[str, Any] = Field(default_factory=dict)
        quality_thresholds: dict[str, Any] = Field(default_factory=dict)
        output_requirements: dict[str, Any] = Field(default_factory=dict)
        provenance_requirements: dict[str, Any] = Field(default_factory=dict)
        payload_digest: str = ""
        runtime_customization_package: Optional[RuntimeCustomizationPackage] = None

else:
    from dataclasses import dataclass, field as dc_field

    @dataclass
    class RuntimeCustomizationPackage:  # type: ignore[no-redef]
        workflow_manifest_ref: str = ""
        runtime_gate_profile_ref: str = ""
        exit_profile_ref: str = ""
        judge_profile_ref: str = ""
        eval_rubric_ref: str = ""
        threshold_profile_ref: str = ""
        grader_roster_ref: str = ""
        rubric_output_map_ref: str = ""
        negative_controls_ref: str = ""
        learning_profile_ref: str = ""
        meta_feedback_profile_ref: str = ""
        prompt_profile_ref: str = ""
        route_profile_ref: str = ""
        retrieval_profile_ref: str = ""
        repair_profile_ref: str = ""
        cache_profile_ref: str = ""
        capability_profile_ref: str = ""
        orchestration_profile_ref: str = ""
        provider_profile_ref: str = ""
        write_policy: str = "read_only"
        required_runtime_gates: tuple = ()
        required_exit_gates: tuple = ()
        conditional_exit_gates: tuple = ()
        package_digest: str = ""

    @dataclass
    class AppsRgIngressContractV1:  # type: ignore[no-redef]
        apps_rg_contract_version: str = APPS_RG_INGRESS_CONTRACT_VERSION
        transport: dict = dc_field(default_factory=dict)
        identity: dict = dc_field(default_factory=dict)
        replay: dict = dc_field(default_factory=dict)
        jd_payload: dict = dc_field(default_factory=dict)
        resume_payload: dict = dc_field(default_factory=dict)
        target: dict = dc_field(default_factory=dict)
        generation_mode: str = "strategic_tailor"
        profile_manifest: dict = dc_field(default_factory=dict)
        quality_thresholds: dict = dc_field(default_factory=dict)
        output_requirements: dict = dc_field(default_factory=dict)
        provenance_requirements: dict = dc_field(default_factory=dict)
        payload_digest: str = ""
        runtime_customization_package: Any = None
