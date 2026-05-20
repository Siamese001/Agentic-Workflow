"""W7A — quarantine product-shaped shadow paths (SP-001/002/003) from core proof consumption."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from apps_rg.runtime.non_product_proof_stamp import (
    DEMO_HARNESS_PROOF_CLASSIFICATION,
    FORBIDDEN_PRODUCT_PROOF_CLASSIFICATIONS,
    ORCHESTRATOR_PROOF_CLASSIFICATION,
    PACKAGE_DISPOSITION_CLASSIFICATION,
    is_eligible_for_product_or_l7_certification,
)

SHADOW_PATH_ARTIFACT_SPECS: dict[str, str] = {
    "orchestrator_non_product_receipt.json": ORCHESTRATOR_PROOF_CLASSIFICATION,
    "resume_package_x3.json": PACKAGE_DISPOSITION_CLASSIFICATION,
    "resume_package_receipt.json": PACKAGE_DISPOSITION_CLASSIFICATION,
    "resume_package_manifest.json": PACKAGE_DISPOSITION_CLASSIFICATION,
    "demo_harness_proof.json": DEMO_HARNESS_PROOF_CLASSIFICATION,
}

SHADOW_PATH_EXPLICIT_NON_CLAIMS: tuple[str, ...] = (
    "shadow path artifacts are offline or dev harness evidence only",
    "orchestrator rollup is not integrated R4 product runtime proof",
    "package rollup X3 is not agentic_core Exit X3",
    "demo harness output is not canonical python -m apps_rg section proof",
)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        return doc if isinstance(doc, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _proof_class_from_blob(blob: Mapping[str, Any]) -> str:
    return str(
        blob.get("proof_classification")
        or blob.get("package_disposition_classification")
        or ""
    ).strip()


def assess_shadow_product_shaped_artifacts(
    artifact_dir: Path,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Return untrusted shadow artifacts present under a proof directory."""
    artifact_dir = Path(artifact_dir)
    untrusted: list[dict[str, str]] = []
    classifications: dict[str, str] = {}
    present_any = False

    for filename, expected_pc in SHADOW_PATH_ARTIFACT_SPECS.items():
        path = artifact_dir / filename
        if not path.is_file():
            continue
        present_any = True
        blob = _load_json(path)
        found_pc = _proof_class_from_blob(blob) or expected_pc
        classifications[filename] = found_pc
        untrusted.append(
            {
                "artifact": filename,
                "reason": f"shadow_path_SP:{found_pc}:not_core_product_proof",
                "proof_classification": found_pc,
            }
        )

    legacy_x3 = artifact_dir / "resume_package_x3_disposition.json"
    if legacy_x3.is_file():
        present_any = True
        blob = _load_json(legacy_x3)
        found_pc = _proof_class_from_blob(blob) or PACKAGE_DISPOSITION_CLASSIFICATION
        classifications[str(legacy_x3.name)] = found_pc
        untrusted.append(
            {
                "artifact": legacy_x3.name,
                "reason": "shadow_path_SP-003:package_x3_not_exit_x3",
                "proof_classification": found_pc,
            }
        )

    consumes_as_core_proof = False
    if present_any:
        consumes_as_core_proof = any(
            is_eligible_for_product_or_l7_certification(_load_json(artifact_dir / fn))
            for fn in SHADOW_PATH_ARTIFACT_SPECS
            if (artifact_dir / fn).is_file()
        )

    rel_root = None
    if repo_root is not None:
        try:
            rel_root = artifact_dir.resolve().relative_to(Path(repo_root).resolve()).as_posix()
        except ValueError:
            rel_root = str(artifact_dir)

    return {
        "shadow_paths_present": present_any,
        "shadow_artifact_classifications": classifications,
        "untrusted": untrusted,
        "consumes_shadow_as_core_proof": consumes_as_core_proof,
        "artifact_dir": rel_root,
        "explicit_non_claims": list(SHADOW_PATH_EXPLICIT_NON_CLAIMS) if present_any else [],
        "forbidden_product_proof_classifications": sorted(FORBIDDEN_PRODUCT_PROOF_CLASSIFICATIONS),
    }


def reject_shadow_payload_as_integrated_proof(
    payload: Mapping[str, Any] | None,
    *,
    context: str = "",
) -> None:
    """Raise when a shadow/offline stamp is presented as integrated product proof."""
    if not payload or not isinstance(payload, Mapping):
        return
    pc = _proof_class_from_blob(payload)
    if pc in FORBIDDEN_PRODUCT_PROOF_CLASSIFICATIONS:
        label = context or "shadow_path_quarantine"
        raise ValueError(f"{label}: forbidden product proof classification {pc!r}")
    from apps_rg.runtime.non_product_proof_stamp import guard_reject_non_product_for_certification

    guard_reject_non_product_for_certification(payload, context=context)


__all__ = [
    "SHADOW_PATH_ARTIFACT_SPECS",
    "SHADOW_PATH_EXPLICIT_NON_CLAIMS",
    "assess_shadow_product_shaped_artifacts",
    "reject_shadow_payload_as_integrated_proof",
]
